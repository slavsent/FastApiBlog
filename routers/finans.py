from fastapi.responses import JSONResponse
from os import getcwd, remove
import pandas as pd
from io import BytesIO, StringIO

from Schemas.blogs import PostDetailsModel, PostModel, PostLike, PostDetailsModelLike
from Schemas.users import User
from utils import blogs as post_utils
from utils import users as user_utils
from utils.dependencies import get_current_user, get_current_user_
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from core.db import get_db
import psycopg2
from psycopg2 import Error

router = APIRouter()

try:
    # Подключиться к существующей базе данных
    connection = psycopg2.connect(user="postgres",
                                  password="space",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="finans_db")
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    загрузка файла
    """
    # Создайтся курсор для выполнения операций с базой данных
    cursor = connection.cursor()
    # SQL-запрос для создания новой таблицы
    create_table_tree = f'''DO $$
                            BEGIN
                            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE TYPNAME = 'admin_level') THEN 
                            CREATE TYPE  admin_level AS ENUM ('lavel_1', 'lavel_2', 'lavel_3');
                            END IF;
                            END;
                            $$;
                            CREATE TABLE IF NOT EXISTS tree_data (
                            id TEXT  PRIMARY KEY,
                            name TEXT,
                            project TEXT,
                            lavel admin_level,
                            parent TEXT REFERENCES tree_data(id)
                            version varchar(10),
                            sum_years float8
                            ); 
                            CREATE TABLE IF NOT EXISTS finans_data
                                  (ID SERIAL  PRIMARY KEY,
                                  year_data INT,
                                  fin_data float8,
                                  version varchar(10),
                                  id_tree TEXT,
                                  FOREIGN KEY (id_tree) REFERENCES tree_data (id) ON UPDATE CASCADE ON DELETE CASCADE
                                  ); '''
    # Выполнение команды: это создает новуые таблицы
    cursor.execute(create_table_tree)
    connection.commit()

    print("Таблица успешно создана в PostgreSQL")
    version = ''.join(str(file.filename).split('.'))
    postgreSQL_select_Query = f'''select *
                                        from finans_data 
                                        where version = '{version}'
                                        ;
                                      '''
    cursor.execute(postgreSQL_select_Query)
    mobile_records = cursor.fetchall()
    if len(mobile_records) == 0:

        contents = file.file.read()
        data = BytesIO(contents)
        df = pd.read_csv(data, encoding='ISO-8859-1', sep='[;]', engine='python')
        for i in range(len(df)):
            name = df.loc[i].cod
            project = df.loc[i].project
            on_id = ''.join(str(file.filename).split('.')) + ''.join(name.split('.'))
            on_lavel = name.split('.')
            if len(on_lavel) < 2:
                lavel = 'lavel_1'
                parent = 'NULL'
            elif len(on_lavel) == 2:
                lavel = 'lavel_2'
                parent = on_id[:-1]
            else:
                lavel = 'lavel_3'
                parent = on_id[:-1]
            on_version = ''.join(str(file.filename).split('.'))
            try:
                if parent == 'NULL':
                    add_data = f"INSERT INTO tree_data (id, name, project, lavel, parent) VALUES ('{on_id}', '{name}', '{project}', '{lavel}', {parent});"
                else:
                    add_data = f"INSERT INTO tree_data (id, name, project, lavel, parent) VALUES ('{on_id}', '{name}', '{project}', '{lavel}', '{parent}');"
                cursor.execute(add_data)
                connection.commit()
            except Exception:
                connection.rollback()

            for col, data in df.items():
                try:
                    key_year = int(col)
                except Exception:
                    continue
                if len(col) == 4:
                    if str(df.loc[i][col]) == 'nan':
                        add_data_fin = f"INSERT INTO finans_data (id_tree, year_data, fin_data, version) VALUES ('{on_id}', {int(col)}, 0, '{on_version}');"
                    else:
                        add_data_fin = f"INSERT INTO finans_data (id_tree, year_data, fin_data, version) VALUES ('{on_id}', {int(col)}, {df.loc[i][col]}, '{on_version}');"
                    cursor.execute(add_data_fin)
                    connection.commit()
        # connection.close()
        data.close()
        file.file.close()
    return JSONResponse(content={"filename": str(file.filename)}, status_code=200)


@router.get("/download/{name_file}")
def download_file(name_file: str):
    """
    загрузка файла с сервера
    :param name_file:
    :return:
    """
    return FileResponse(path=getcwd() + "/" + name_file, media_type='application/octet-stream', filename=name_file)


@router.get("/file/{name_file}")
def get_file(name_file: str):
    """
    получение файла с сервера
    :param name_file:
    :return:
    """
    version = ''.join(name_file.split('.'))
    df_new = pd.read_sql(f'''select 
                                        finans_data.year_data as year,
                                        finans_data.fin_data as finans,
                                        tree.id,
                                        tree.name,
                                        tree.project,
                                        tree.lavel,
                                        tree.parent
                                        from finans_data 
                                        left join  tree_data as tree
                                        on finans_data.id_tree = tree.id 
                                        where finans_data.version = '{version}'
                                        ;
                                      ''', connection)
    year = list(df_new.year.unique())
    ogl = ['cod', 'project'] + year
    cod = list(df_new.name.unique())
    project = []
    cod_try = []
    for i in range(len(cod)):
        for j in range(len(df_new)):
            if df_new.loc[j, 'name'] == cod[i] and (not cod[i] in cod_try):
                project.append(df_new.loc[j].project)
                cod_try.append(cod[i])

    data_year = {}
    for i in range(len(cod)):
        for el in year:
            if el in data_year:
                data_year[el].append(0)
            else:
                data_year[el] = [0]

        if len(cod[i]) == 1:
            for j in range(len(df_new)):
                if cod[i] == df_new.loc[j, 'name'][0]:
                    data_year[df_new.loc[j, 'year']][i] += df_new.loc[j, 'finans']
        elif len(cod[i]) == 3:
            for j in range(len(df_new)):
                if cod[i] == df_new.loc[j, 'name'][0:3]:
                    data_year[df_new.loc[j, 'year']][i] += df_new.loc[j, 'finans']
        else:
            for j in range(len(df_new)):
                if cod[i] == df_new.loc[j, 'name']:
                    data_year[df_new.loc[j, 'year']][i] = df_new.loc[j, 'finans']

    data = {}
    for el in ogl:
        if el == 'cod':
            data[el] = cod
        elif el == 'project':
            data[el] = project
    data_end = data | data_year
    df_end = pd.DataFrame(data_end)
    df_end.to_csv('file1.csv', index=False)
    return FileResponse(path=getcwd() + "/file1.csv")


@router.delete("/delete/file/{name_file}")
def delete_file(name_file: str):
    """
    удаление файла с сервера
    :param name_file:
    :return:
    """
    try:
        remove(getcwd() + "/" + name_file)
        return JSONResponse(content={
            "removed": True
        }, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={
            "removed": False,
            "error_message": "File not found"
        }, status_code=404)
