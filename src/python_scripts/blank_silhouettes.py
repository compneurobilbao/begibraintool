import os
from PIL import Image, ImageChops, ImageOps

print(">>> Importando backgroundremover...")
from backgroundremover.bg import remove
print(">>> backgroundremover importado correctamente")


# Forzar ruta del modelo ya descargado
os.environ["U2NET_HOME"] = r"C:\Users\akoun\.u2net"


# ---------------------------
# 1. Quitar fondo y conservar sujeto
# ---------------------------
def remove_background(src_img_path, output_dir):
    subject_dir = os.path.join(output_dir, "subject")
    os.makedirs(subject_dir, exist_ok=True)

    img_name = os.path.splitext(os.path.basename(src_img_path))[0] + ".png"
    out_img_path = os.path.join(subject_dir, img_name)

    with open(src_img_path, "rb") as f:
        img_data = f.read()
        removed_bg = remove(img_data)

    with open(out_img_path, "wb") as f:
        f.write(removed_bg)

    print(f"[OK] Fondo removido: {out_img_path}")
    return out_img_path

# ---------------------------
# 2. Eliminar sujeto dejando solo el fondo
# ---------------------------
def remove_subject(src_img_path, bg_removed_path, output_dir):
    background_dir = os.path.join(output_dir, "background")
    os.makedirs(background_dir, exist_ok=True)

    img_name = os.path.splitext(os.path.basename(src_img_path))[0] + "_no_subject.png"
    out_img_path = os.path.join(background_dir, img_name)

    original = Image.open(src_img_path).convert("RGBA")
    img_removed = Image.open(bg_removed_path).convert("RGBA")
    background = ImageChops.subtract(original, img_removed)
    background.save(out_img_path, "PNG")

    print(f"[OK] Fondo extraído: {out_img_path}")
    return out_img_path

# ---------------------------
# 3. Convertir imagen a blanco y negro
# ---------------------------
def convert_to_bw(src_img_path, output_dir):
    raw_bw_dir = os.path.join(output_dir, "raw_BW")
    os.makedirs(raw_bw_dir, exist_ok=True)

    img = Image.open(src_img_path)
    bw_img = ImageOps.grayscale(img)

    img_name = os.path.splitext(os.path.basename(src_img_path))[0] + "_bw.png"
    out_img_path = os.path.join(raw_bw_dir, img_name)
    bw_img.save(out_img_path)

    print(f"[OK] Imagen B/N: {out_img_path}")
    return out_img_path

# ---------------------------
# 4. Convertir fondo a B/N
# ---------------------------
def convert_background_to_bw(src_img_path, bg_removed_path, output_dir):
    background_bw_dir = os.path.join(output_dir, "background_BW")
    os.makedirs(background_bw_dir, exist_ok=True)

    original = Image.open(src_img_path).convert("RGBA")
    bg_removed = Image.open(bg_removed_path).convert("RGBA")
    background = ImageChops.subtract(original, bg_removed)
    bw_background = ImageOps.grayscale(background)

    img_name = os.path.splitext(os.path.basename(src_img_path))[0] + "_background_bw.png"
    out_img_path = os.path.join(background_bw_dir, img_name)
    bw_background.save(out_img_path)

    print(f"[OK] Fondo B/N: {out_img_path}")
    return out_img_path

# ---------------------------
# 5. Convertir sujeto a B/N
# ---------------------------
def convert_subject_to_bw(bg_removed_path, output_dir):
    subject_bw_dir = os.path.join(output_dir, "subject_BW")
    os.makedirs(subject_bw_dir, exist_ok=True)

    img = Image.open(bg_removed_path).convert("RGBA")
    bw_subject = ImageOps.grayscale(img)

    img_name = os.path.splitext(os.path.basename(bg_removed_path))[0] + "_subject_bw.png"
    out_img_path = os.path.join(subject_bw_dir, img_name)
    bw_subject.save(out_img_path)

    print(f"[OK] Sujeto B/N: {out_img_path}")
    return out_img_path

# ---------------------------
# 6. Crear silueta del sujeto
# ---------------------------
def create_silhouette(bg_removed_path, output_dir):
    silhouette_dir = os.path.join(output_dir, "silhouette")
    os.makedirs(silhouette_dir, exist_ok=True)

    img = Image.open(bg_removed_path).convert("RGBA")
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if a != 0:
                pixels[x, y] = (0, 0, 0, 255)

    img_name = os.path.splitext(os.path.basename(bg_removed_path))[0] + ".png"#+ "_silhouette.png"
    out_img_path = os.path.join(silhouette_dir, img_name)
    img.save(out_img_path)

    print(f"[OK] Silueta creada: {out_img_path}")
    return out_img_path

# ---------------------------
# 7. Crear mosaico de una carpeta
# ---------------------------
def create_mosaic(folder_path, tile_size=(100, 100), padding=10):
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    if not image_files:
        return

    grid_size = int(len(image_files) ** 0.5) + 1
    mosaic_width = grid_size * tile_size[0] + (grid_size + 1) * padding
    mosaic_height = grid_size * tile_size[1] + (grid_size + 1) * padding
    mosaic_image = Image.new('RGB', (mosaic_width, mosaic_height), (255, 255, 255))

    for idx, img_path in enumerate(image_files):
        row, col = divmod(idx, grid_size)
        img = Image.open(img_path).resize(tile_size)
        x_offset = col * tile_size[0] + (col + 1) * padding
        y_offset = row * tile_size[1] + (row + 1) * padding
        mosaic_image.paste(img, (x_offset, y_offset))

    mosaic_path = os.path.join(folder_path, 'mosaic.jpg')
    mosaic_image.save(mosaic_path)
    print(f"[OK] Mosaico: {mosaic_path}")
    return mosaic_path

# ---------------------------
# 8. Procesar todas las imágenes manteniendo estructura
# ---------------------------
def process_images(raw_dir, output_dir, apply_bw=False, apply_subject_removal=False, apply_bg_bw=False, apply_subject_bw=False, apply_silhouette_creation=False):
    for root, _, files in os.walk(raw_dir):
        for file in files:
            if ( # Check that the file is a valid image
                file.lower().endswith(('.png', '.jpg', '.jpeg'))
                and not file.startswith("._")
                #and os.path.getsize(os.path.join(raw_dir, file)) > 0
            ):
                
                src_img_path = os.path.join(root, file)
                relative_dir = os.path.relpath(root, raw_dir)
                output_subdir = os.path.join(output_dir, relative_dir)

                # Guardar copia en "raw"
                raw_dir_copy = os.path.join(output_subdir, "raw")
                os.makedirs(raw_dir_copy, exist_ok=True)
                
                Image.open(src_img_path).save(os.path.join(raw_dir_copy, file))

                # Quitar fondo y guardar sujeto
                bg_removed_path = remove_background(src_img_path, output_subdir)

                if apply_subject_removal:
                    remove_subject(src_img_path, bg_removed_path, output_subdir)

                if apply_bw:
                    convert_to_bw(src_img_path, output_subdir)

                if apply_bg_bw:
                    convert_background_to_bw(src_img_path, bg_removed_path, output_subdir)

                if apply_subject_bw:
                    convert_subject_to_bw(bg_removed_path, output_subdir)

                if apply_silhouette_creation:
                    create_silhouette(bg_removed_path, output_subdir)

                create_mosaic(output_subdir)

# ---------------------------
# Uso
# ---------------------------
# raw_dir = r"C:\Users\akoun\Desktop\Biocruces\2.DATASETS\begibraintool_image_selection\03_ANIMALES_AnimalDB"
# output_dir = r"C:\Users\akoun\Desktop\Biocruces\2.DATASETS\begibraintool_image_selection\03_ANIMALES_AnimalDB_SEGMENTADOS"

# process_images(
#     raw_dir,
#     output_dir,
#     apply_bw=False,
#     apply_subject_removal=True,
#     apply_bg_bw=False,
#     apply_subject_bw=False,
#     apply_silhouette_creation=True
# )
