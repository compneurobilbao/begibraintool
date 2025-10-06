# python_scripts/spatial_frequencies.py
import os
import numpy as np
from skimage import io, img_as_ubyte

def cpd_to_radius(cpd, image_width, screen_width_cm, distance_to_screen_cm, dpi):
    """Convierte CPD a radios en el espectro de Fourier."""
    pixels_per_cm = dpi / 2.54
    pixels_per_degree = (distance_to_screen_cm * np.tan(np.radians(1))) * pixels_per_cm
    cycles_per_pixel = cpd / pixels_per_degree
    return int(cycles_per_pixel * (image_width / 2))

def normalize_image(image):
    """Normaliza la imagen al rango 0-255 (uint8)."""
    image_normalized = np.real(image)
    image_normalized -= image_normalized.min()
    image_normalized /= image_normalized.max()
    return img_as_ubyte(image_normalized)

def bandpass_filter_image(image, mask, min_cpd, max_cpd, image_width, screen_width_cm, distance_to_screen_cm, dpi):
    """Aplica un filtro paso banda entre min_cpd y max_cpd."""
    min_radius = cpd_to_radius(min_cpd, image_width, screen_width_cm, distance_to_screen_cm, dpi)
    max_radius = cpd_to_radius(max_cpd, image_width, screen_width_cm, distance_to_screen_cm, dpi)

    # Fourier Transform
    f_transform = np.fft.fft2(image * mask)
    f_transform_shifted = np.fft.fftshift(f_transform)

    # Crear máscara paso banda
    rows, cols = image.shape
    crow, ccol = rows // 2, cols // 2
    y, x = np.ogrid[:rows, :cols]
    distance_squared = (x - ccol) ** 2 + (y - crow) ** 2

    bandpass_mask = np.logical_and(distance_squared >= min_radius**2, distance_squared <= max_radius**2).astype(float)

    # Aplicar filtro
    bandpass_frequencies = f_transform_shifted * bandpass_mask

    # Transformada inversa
    filtered_image = np.fft.ifft2(np.fft.ifftshift(bandpass_frequencies))

    return normalize_image(filtered_image)

def apply_bandpass_filters(image, mask, cpd_ranges, output_dir, rel_path, image_file, image_width, screen_width_cm, distance_to_screen_cm, dpi):
    """Aplica todos los filtros paso banda definidos en cpd_ranges a una imagen."""
    for (min_cpd, max_cpd) in cpd_ranges:
        # El bandpass va DENTRO de la categoría (animals, objects, etc.)
        band_output_dir = os.path.join(output_dir, rel_path, f"bandpass_{min_cpd}_{max_cpd}_cpd")
        os.makedirs(band_output_dir, exist_ok=True)

        filtered_image = bandpass_filter_image(
            image, mask, min_cpd, max_cpd, image_width,
            screen_width_cm, distance_to_screen_cm, dpi
        )

        io.imsave(os.path.join(band_output_dir, image_file), filtered_image)
        print(f"[SPATIAL FREQ] Processed {rel_path}/{image_file} with CPD {min_cpd}-{max_cpd}")


def extract_from_folder(input_dir, output_dir, cpd_ranges, screen_width_cm, distance_to_screen_cm, dpi):
    """Procesa todas las imágenes de input_dir y guarda filtros en output_dir replicando la estructura de carpetas."""
    for root, _, files in os.walk(input_dir):
        for image_file in files:
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_path = os.path.join(root, image_file)
                image = io.imread(image_path, as_gray=True)
                mask = np.ones_like(image)

                # Ruta relativa (ej. "animals" o "objects/subfolder")
                rel_path = os.path.relpath(root, input_dir)

                apply_bandpass_filters(
                    image, mask, cpd_ranges, output_dir, rel_path,
                    image_file, image.shape[1], screen_width_cm,
                    distance_to_screen_cm, dpi
                )
