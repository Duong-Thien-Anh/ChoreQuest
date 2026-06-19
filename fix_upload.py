content = open('backend/routers/chores.py').read()

old = '        upload_dir = "/app/data/uploads"\n        os.makedirs(upload_dir, exist_ok=True)\n        ext = os.path.splitext(file.filename or "photo.jpg")[1] or ".jpg"\n        filename = f"{uuid.uuid4().hex}{ext}"\n        filepath = os.path.join(upload_dir, filename)\n        with open(filepath, "wb") as f:\n            f.write(contents)\n        assignment.photo_proof_path = filename'

new = '        import cloudinary\n        import cloudinary.uploader\n        import io\n        cloudinary.config(\n            cloud_name=settings.CLOUDINARY_CLOUD_NAME,\n            api_key=settings.CLOUDINARY_API_KEY,\n            api_secret=settings.CLOUDINARY_API_SECRET,\n        )\n        result = cloudinary.uploader.upload(\n            io.BytesIO(contents),\n            folder="chorequest/uploads",\n            resource_type="image",\n        )\n        assignment.photo_proof_path = result["secure_url"]'

if old in content:
    content = content.replace(old, new)
    open('backend/routers/chores.py', 'w').write(content)
    print('Done')
else:
    print('ERROR: old string not found')
