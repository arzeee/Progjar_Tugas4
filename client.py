import requests

def list_files(server_url):
    try:
        response = requests.get(f"{server_url}/list")
        print("== Daftar File ==")
        print(response.text)
    except Exception as e:
        print(f"[ERROR] Tidak dapat mengambil daftar file: {e}")

def upload_file(server_url, filepath):
    try:
        filename = filepath.split('/')[-1]
        with open(filepath, 'r') as file:
            data = file.read()

        headers = {'X-Filename': filename}
        response = requests.post(f"{server_url}/upload", headers=headers, data=data)
        print(response.text)
    except FileNotFoundError:
        print(f"[ERROR] File '{filepath}' tidak ditemukan.")
    except Exception as e:
        print(f"[ERROR] Upload gagal: {e}")

def delete_file(server_url, filename):
    try:
        response = requests.delete(f"{server_url}/delete?filename={filename}")
        print(response.text)
    except Exception as e:
        print(f"[ERROR] Gagal menghapus file: {e}")

def main():
    server_ip = input("Masukkan IP server (contoh: 192.168.1.10): ").strip()
    server_url = f"http://{server_ip}:8889"

    while True:
        print("\n=== Menu Client ===")
        print("1. Lihat daftar file")
        print("2. Upload file")
        print("3. Hapus file")
        print("4. Keluar")
        choice = input("Pilih operasi [1-4]: ").strip()

        if choice == '1':
            list_files(server_url)
        elif choice == '2':
            filepath = input("Masukkan path file yang akan diupload: ").strip()
            upload_file(server_url, filepath)
        elif choice == '3':
            filename = input("Masukkan nama file yang akan dihapus: ").strip()
            delete_file(server_url, filename)
        elif choice == '4':
            print("Keluar.")
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()

