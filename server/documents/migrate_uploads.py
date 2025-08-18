from documents.storage import migrate_from_public_uploads

if __name__ == "__main__":
    migrate_from_public_uploads()
    print("Migración completada")
