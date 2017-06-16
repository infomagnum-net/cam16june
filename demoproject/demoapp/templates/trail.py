import face_recognition

known_image = face_recognition.load_image_file("/home/zoom/Desktop/testingggg/222.jpg")
unknown_image = face_recognition.load_image_file("/home/zoom/Desktop/1.jpg")
biden_encoding = face_recognition.face_encodings(known_image)[0]
unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

print '******************'
print biden_encoding
print '******************'
print unknown_encoding

results = face_recognition.compare_faces([biden_encoding], unknown_encoding)