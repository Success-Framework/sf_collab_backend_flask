import pymysql

try:
    conn = pymysql.connect(
        host="mysql-367e2d56-mohameddhimni311-06d1.f.aivencloud.com",
        user="avnadmin",
        password="AVNS_uAktzkL2Vx2kybgbYSp",
        port=22525,
        ssl={"ssl": {}}
    )
    print("Connected!")
    with conn.cursor() as c:
        c.execute("SELECT NOW();")
        print(c.fetchone())
except Exception as e:
    print("ERROR:", e)
