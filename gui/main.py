import os
import customtkinter as ctk

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

root = ctk.CTk()

def get_images():
    result = os.popen("docker image ls").readlines()
    images = []
    for l in result[1:]:
        line = l.strip("\n")
        images.append(line.split()[0])
    images = images[:-1]
    textBox.insert(ctk.END, images)
    textBox.delete(ctk.END)
    return images

# Top and Bottom frames
frame_top = ctk.CTkFrame(master=root)
frame_top.pack(pady=10, padx=20, fill="both", expand=True)

frame_bottom = ctk.CTkFrame(master=root)
frame_bottom.pack(side="bottom", pady=10, padx=20, fill="both", expand=True)

# Installation
frame_install = ctk.CTkFrame(master=frame_top)
frame_install.pack(side="left", pady=10, padx=20, fill="both", expand=True)

label_cv = ctk.CTkLabel(master=frame_install, text="Cardiovision")
button_install = ctk.CTkButton(master=frame_install, height=80, text="Install", fg_color="blue", command=get_images)

label_cv.grid(row=0, column=0, pady=12, padx=10)
button_install.grid(row=1, column=0, pady=12, padx=10)


# training
frame_train = ctk.CTkFrame(master=frame_top)
frame_train.pack(side="left", pady=10, padx=20, fill="both", expand=True)

label_training = ctk.CTkLabel(master=frame_train, text="Training CV")
button_import = ctk.CTkButton(master=frame_train, text="Import", command=get_images)
button_train = ctk.CTkButton(master=frame_train, text="Train", command=get_images)

label_training.pack(pady=12, padx=10)
button_import.pack(pady=12, padx=10)
button_train.pack(pady=12, padx=10)

# Running
frame_running = ctk.CTkFrame(master=frame_top)
frame_running.pack(side="left", pady=10, padx=20, fill="both", expand=True)

options_list = ["Digital Twin", "Left Venctricle"]
#TODO It should update the list automatically based on the weights exist in the CNN code
# value_inside = ctk.StringVar(root)
# value_inside.set("Select a component")

label_training = ctk.CTkLabel(frame_running, text="Prediction & Analysis")
button_prediction = ctk.CTkButton(frame_running, text="Prediction", command=get_images)
button_component = ctk.CTkOptionMenu(master=frame_running, values=options_list)

label_training.pack(pady=12, padx=10)
button_component.pack(pady=12, padx=10)
button_prediction.pack(pady=12, padx=10)



# outputs
frame_outputs = ctk.CTkFrame(master=frame_bottom)
frame_outputs.pack(side="bottom", pady=10, padx=20, fill="both", expand=True)

textBox = ctk.CTkTextbox(master=frame_outputs)
textBox.pack(pady=12, padx=10)

root.mainloop()
