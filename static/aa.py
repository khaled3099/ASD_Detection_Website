# Example file path
file_path = "Nouveau dossier (6)/Autistic.56.jpg"

# Find the index of '/' in the file path
index = file_path.find('/')

# Remove everything before the first '/'
if index != -1:
    filename = file_path[index + 1:]
else:
    filename = file_path

# Print the extracted filename
print("Extracted filename:", filename)
