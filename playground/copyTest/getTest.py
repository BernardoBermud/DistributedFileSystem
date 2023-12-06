import os

def copy_file_in_chunks(source_path1, source_path2, destination_path):
    if os.path.isfile(source_path1) and os.path.isfile(source_path2):    
        file1Stat = os.stat(source_path1)
        size1 = file1Stat.st_size
        
        file2Stat = os.stat(source_path2)
        size2 = file2Stat.st_size

        try:
            # Initialize an array to store file chunks
            file_chunks = []
            #data_nodes = 2
            #chunk_size = size//data_nodes
            # Read the file in chunks
            
            with open(source_path1, 'rb') as source_file:
                chunk = source_file.read(size1)
                file_chunks.append(chunk)
            with open(source_path2, 'rb') as source_file:
                chunk = source_file.read(size2)
                file_chunks.append(chunk)

            # Create a new file and write the chunks
            
            with open(destination_path, 'wb') as destination_file:
                for chunk in file_chunks:
                    destination_file.write(chunk)
            
                
            print(f"Memorie copied to {destination_path}")

        except FileNotFoundError:
            print("Source file not found.")
        except Exception as e:
            print(f"Error: {e}")

# Example usage with a specified chunk size (in bytes)
source1 = 'file1'
source2 = 'file2'
destination_file_path = 'popo.mp4'

copy_file_in_chunks(source1, source2, destination_file_path)