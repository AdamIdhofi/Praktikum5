# Method untuk menangani permintaan GET pada endpoint root ("/")
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Method untuk menangani permintaan GET pada endpoint "/mahasiswa/{nim}"
@app.get("/mahasiswa/{nim}")
def ambil_mhs(nim:str):
    return {"nama": "Budi Martami"}

# Method untuk menangani permintaan GET pada endpoint "/mahasiswa2/"
@app.get("/mahasiswa2/")
def ambil_mhs2(nim:str):
    return {"nama": "Budi Martami 2"}

# Method untuk menangani permintaan GET pada endpoint "/daftar_mhs/"
@app.get("/daftar_mhs/")
def daftar_mhs(id_prov:str,angkatan:str):
    return {"query":" idprov: {}  ; angkatan: {} ".format(id_prov,angkatan),"data":[{"nim":"1234"},{"nim":"1235"}]}

# Method untuk menangani permintaan GET pada endpoint "/init/"
@app.get("/init/")
def init_db():
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        create_table = """ CREATE TABLE mahasiswa(
                ID      	INTEGER PRIMARY KEY 	AUTOINCREMENT,
                nim     	TEXT            	NOT NULL,
                nama    	TEXT            	NOT NULL,
                id_prov 	TEXT            	NOT NULL,
                angkatan	TEXT            	NOT NULL,
                tinggi_badan  INTEGER
            )  
            """
        cur.execute(create_table)
        con.commit
    except:
        return ({"status":"terjadi error"})  
    finally:
        con.close()
      
    return ({"status":"ok, db dan tabel berhasil dicreate"})

# Method untuk menangani permintaan POST pada endpoint "/tambah_mhs/"
@app.post("/tambah_mhs/", response_model=Mhs,status_code=201)  
def tambah_mhs(m: Mhs,response: Response, request: Request):
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        # Hanya untuk test, rawal sql injection, gunakan spt SQLAlchemy
        cur.execute("""insert into mahasiswa (nim,nama,id_prov,angkatan,tinggi_badan) values ( "{}","{}","{}","{}",{})""".format(m.nim,m.nama,m.id_prov,m.angkatan,m.tinggi_badan))
        con.commit() 
    except:
        print("oioi error")
        return ({"status":"terjadi error"})   
    finally:  	 
        con.close()
    response.headers["Location"] = "/mahasiswa/{}".format(m.nim) 
    print(m.nim)
    print(m.nama)
    print(m.angkatan)
  
    return m

# Method untuk menangani permintaan GET pada endpoint "/tampilkan_semua_mhs/"
@app.get("/tampilkan_semua_mhs/")
def tampil_semua_mhs():
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        recs = []
        for row in cur.execute("select * from mahasiswa"):
            recs.append(row)
    except:
        return ({"status":"terjadi error"})   
    finally:  	 
        con.close()
    return {"data":recs}

# Method untuk menangani permintaan PUT pada endpoint "/update_mhs_put/{nim}"
@app.put("/update_mhs_put/{nim}",response_model=Mhs)
def update_mhs_put(response: Response,nim: str, m: Mhs ):
    # Update keseluruhan
    # Karena key, nim tidak diupdate
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("select * from mahasiswa where nim = ?", (nim,) )  # Tambah koma untuk menandakan tupple
        existing_item = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
    
    if existing_item:  # Data ada 
        print(m.tinggi_badan)
        cur.execute("update mahasiswa set nama = ?, id_prov = ?, angkatan=?, tinggi_badan=? where nim=?", (m.nama,m.id_prov,m.angkatan,m.tinggi_badan,nim))
        con.commit()            
        response.headers["location"] = "/mahasiswa/{}".format(m.nim)
    else:  # Data tidak ada
        print("item not foud")
        raise HTTPException(status_code=404, detail="Item Not Found")
      
    con.close()
    return m

# Method untuk menangani permintaan PATCH pada endpoint "/update_mhs_patch/{nim}"
@app.patch("/update_mhs_patch/{nim}",response_model = MhsPatch)
def update_mhs_patch(response: Response, nim: str, m: MhsPatch ):
    try:
        print(str(m))
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor() 
        cur.execute("select * from mahasiswa where nim = ?", (nim,) )  # Tambah koma untuk menandakan tupple
        existing_item = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # Misal database down  
    
    if existing_item:  # Data ada, lakukan update
        sqlstr = "update mahasiswa set " # Asumsi minimal ada satu field update
        # Todo: bisa direfaktor dan dirapikan
        if m.nama!="kosong":
            if m.nama!=None:
                sqlstr = sqlstr + " nama = '{}' ,".format(m.nama)
            else:     
                sqlstr = sqlstr + " nama = null ,"
        
        if m.angkatan!="kosong":
            if m.angkatan!=None:
                sqlstr = sqlstr + " angkatan = '{}' ,".format(m.angkatan)
            else:
                sqlstr = sqlstr + " angkatan = null ,"
        
        if m.id_prov!="kosong":
            if m.id_prov!=None:
                sqlstr = sqlstr + " id_prov = '{}' ,".format(m.id_prov) 
            else:
                sqlstr = sqlstr + " id_prov = null, "     

        if m.tinggi_badan!=-9999:
            if m.tinggi_badan!=None:
                sqlstr = sqlstr + " tinggi_badan = {} ,".format(m.tinggi_badan)
            else:    
                sqlstr = sqlstr + " tinggi_badan = null ,"

        sqlstr = sqlstr[:-1] + " where nim='{}' ".format(nim)  # Buang koma yang trakhir  
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/mahasixswa/{}".format(nim)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # Data tidak ada 404, item not found
        raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m

# Method untuk menangani permintaan DELETE pada endpoint "/delete_mhs/{nim}"
@app.delete("/delete_mhs/{nim}")
def delete_mhs(nim: str):
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        sqlstr = "delete from mahasiswa  where nim='{}'".format(nim)                 
        print(sqlstr) # Debug 
        cur.execute(sqlstr)
        con.commit()
    except:
        return ({"status":"terjadi error"})   
    finally:  	 
        con.close()
    
    return {"status":"ok"}
