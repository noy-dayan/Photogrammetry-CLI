def count_faces_in_obj(file_path):
    face_count = 0

    try:
        with open(file_path, 'r') as file:
            face_count = sum(1 for line in file if line.startswith('f '))

        return face_count
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example usage
file_path = r'C:\Users\StrikeOver.DESKTOP-HNIMD1Q\Desktop\Photogrammetry-CLI\test\v1\tasks\11_texturing\texturedMesh.obj'
faces = count_faces_in_obj(file_path)
print(f"The number of faces in the OBJ file: {faces}")
