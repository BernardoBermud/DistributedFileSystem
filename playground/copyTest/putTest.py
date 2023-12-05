import os

def copy_file_in_chunks(source_path, destination_path):
    if os.path.isfile(source_path):    
        fileStat = os.stat(source_path)
        size = fileStat.st_size
        print(size)
        try:
            # Initialize an array to store file chunks
            file_chunks = []
            data_nodes = 2
            chunk_size = size//data_nodes
            # Read the file in chunks
            with open(source_path, 'rb') as source_file:
                while True:
                    chunk = source_file.read(chunk_size)
                    if not chunk:
                        break
                    file_chunks.append(chunk)

            # Create a new file and write the chunks
            for chunk in file_chunks:
                    destination_file.write(chunk)
            """
            with open(destination_path, 'wb') as destination_file:
                for chunk in file_chunks:
                    destination_file.write(chunk)
            """
            print(f"File copied from {source_path} to {destination_path}")

        except FileNotFoundError:
            print("Source file not found.")
        except Exception as e:
            print(f"Error: {e}")

# Example usage with a specified chunk size (in bytes)
source_file_path = 'servidorIUPI.png'
destination_file_path = 'popo.png'

copy_file_in_chunks(source_file_path, destination_file_path)