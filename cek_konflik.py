


def get_datas(file_path: str) -> list:
    with open(file_path, "r") as file:
        lines = file.readlines()
    
    my_list = []
    for line in lines[3:-1]:
        datas = line.split("|")
        if datas[2].strip() != "":
            matkul = datas[2].strip()
        my_dict = {
            "matkul": matkul,
            "sks": datas[3].strip(),
            "kelas": datas[4].strip(),
            "dosen": datas[5].strip(),
            "hari": datas[6].strip(),
            "ruang": datas[7].strip()
        }
        my_list.append(my_dict)
    
    return my_list


def check_konflik(file_path):
    my_list = get_datas(file_path)

    konflik = {
        "bentrok_ruangan": 0,
        "bentrok_waktu": 0,
        "bentrok_kelas": 0,
        "total_konflik": 0,
        "bentrok": []
    }
    for i, item_1 in enumerate(my_list):
        hari_1 = item_1['hari'].split(", ") # ['sab2', 'sab3']

        for j, item_2 in enumerate(my_list):
            if j > i:
                hari_2 = item_2['hari'].split(", ") # ['sab1', 'sab2']
                if any(hari for hari in hari_1 if hari in hari_2):
                    if item_1['dosen'] == item_2['dosen']:
                        konflik["bentrok_waktu"] += 1
                        konflik['bentrok'].append(
                            f"bentrok waktu: dosen: {item_1['dosen']} matkul: {item_1['matkul']} kelas: {item_1['kelas']} dengan dosen: {item_2['dosen']} matkul: {item_2['matkul']} kelas: {item_2['kelas']}"
                        )
                        konflik["total_konflik"] += 1
                        break
                    if item_1['ruang'] == item_2['ruang'] and item_1 != "Online":
                        konflik["bentrok_ruangan"] += 1
                        konflik['bentrok'].append(
                            f"bentrok ruangan: dosen: {item_1['dosen']} matkul: {item_1['matkul']} kelas: {item_1['kelas']} dengan dosen: {item_2['dosen']} matkul: {item_2['matkul']} kelas: {item_2['kelas']}"
                        )
                        konflik["total_konflik"] += 1
                        break
                    if item_1['kelas'] != item_2['kelas'] and item_1['matkul'] == item_2['matkul']:
                        konflik["bentrok_kelas"] += 1
                        konflik['bentrok'].append(
                            f"bentrok kelas: dosen: {item_1['dosen']} matkul: {item_1['matkul']} kelas: {item_1['kelas']} dengan dosen: {item_2['dosen']} matkul: {item_2['matkul']} kelas: {item_2['kelas']}"
                        )
                        konflik["total_konflik"] += 1
                        break
                    

    print("Konflik Ruangan: ", konflik['bentrok_ruangan'])
    print("Konflik Waktu: ", konflik['bentrok_waktu'])
    print("Konflik Kelas: ", konflik['bentrok_kelas'])
    print("Total Seluruh Konflik: ", konflik['total_konflik'])
    for item in konflik['bentrok']:
        print(item)
        
check_konflik("hasil.txt")
