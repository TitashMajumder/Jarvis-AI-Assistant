import os
from time import sleep
from PIL import Image
from diffusers import StableDiffusionPipeline
import torch


def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.png" for i in range(1, 5)]

    for image_file in files:
        image_path = os.path.join(folder_path, image_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")


def generate_images(prompt):
    os.makedirs("Data", exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float32,
        safety_checker=None
    )
    pipe = pipe.to(device)

    for i in range(4):
        image = pipe(prompt).images[0]
        filename = f"{prompt.replace(' ', '_')}{i + 1}.png"
        image.save(os.path.join("Data", filename))
        print(f"Image {i + 1} saved")


def GenerateImage(prompt: str):
    generate_images(prompt)
    open_images(prompt)


while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read().strip()

        Prompt, Status = Data.split(",")

        if Status.strip() == "True":
            print("Generating Images...")
            GenerateImage(prompt=Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            break
        else:
            sleep(1)

    except Exception as e:
        print(f"Error: {e}")
        sleep(1)