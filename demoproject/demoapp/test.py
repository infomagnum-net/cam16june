import face_recognition
face_locations = face_recognition.face_locations("/home/zoom/Desktop/Testing/t3.jpeg")
face_encodings = face_recognition.face_encodings(frame, face_locations)
existing_user_img = face_recognition.load_image_file("/home/zoom/Desktop/Testing/t3.jpeg")
existing_user_encoding = face_recognition.face_encodings(existing_user_img)[0]
match = face_recognition.compare_faces([existing_user_encoding], face_encoding)
print match