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
                    if(size > chunk_size):
                        size -= chunk_size
                    else:
                        chunk_size = size
                    
                    chunk = source_file.read(chunk_size)
                    if not chunk:
                        break
                    file_chunks.append(chunk)

            # Create a new files with chunks
            with open("file1", 'wb') as destination_file1:
                #for chunk in file_chunks1:
                destination_file1.write(file_chunks[0])

            # Create and write to the second destination file
            with open("file2", 'wb') as destination_file2:
                #for chunk in file_chunks2:
                destination_file2.write(file_chunks[1])
            
            # with open(destination_path, 'wb') as destination_file:
            #     for chunk in file_chunks:
            #         destination_file.write(chunk)
            
            #print(f"File {source_path} stored")

        except FileNotFoundError:
            print("Source file not found.")
        except Exception as e:
            print(f"Error: {e}")

# Example usage with a specified chunk size (in bytes)
source_file_path = '../BadApple.mp4'
destination_file_path = 'popo.png'

copy_file_in_chunks(source_file_path, destination_file_path)