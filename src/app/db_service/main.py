from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2 import sql

app = FastAPI()

def get_db_connection():
    conn = psycopg2.connect(
        dbname="accidents",
        user="mon_user",
        password="mon_mdp",
        host="db_service", 
        port="5432"
    )
    return conn

class Accident(BaseModel):
    num_acc: int
    mois: int
    jour: int
    lum: int
    agg: int
    int: int
    atm: float
    col: float
    com: int
    dep: int
    hr: int
    mn: int
    catv: int
    choc: float
    manv: float
    num_veh: str
    place: int
    catu: int
    grav: int
    sexe: int
    trajet: float
    an_nais: int
    catr: int
    circ: float
    nbv: int
    prof: float
    plan: float
    lartpc: int
    larrout: int
    surf: float
    situ: float

@app.get("/accidents/{accident_id}", response_model=Accident)
def get_accident(accident_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql.SQL("SELECT * FROM accident_data WHERE num_acc = %s"), [accident_id])
    accident = cur.fetchone()
    cur.close()
    conn.close()

    if accident is None:
        raise HTTPException(status_code=404, detail="Accident not found")

    return {
        "num_acc": accident[0],
        "mois": accident[1],
        "jour": accident[2],
        "lum": accident[3],
        "agg": accident[4],
        "int": accident[5],
        "atm": accident[6],
        "col": accident[7],
        "com": accident[8],
        "dep": accident[9],
        "hr": accident[10],
        "mn": accident[11],
        "catv": accident[12],
        "choc": accident[13],
        "manv": accident[14],
        "num_veh": accident[15],
        "place": accident[16],
        "catu": accident[17],
        "grav": accident[18],
        "sexe": accident[19],
        "trajet": accident[20],
        "an_nais": accident[21],
        "catr": accident[22],
        "circ": accident[23],
        "nbv": accident[24],
        "prof": accident[25],
        "plan": accident[26],
        "lartpc": accident[27],
        "larrout": accident[28],
        "surf": accident[29],
        "situ": accident[30],
    }