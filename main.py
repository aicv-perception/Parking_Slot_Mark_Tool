import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import json
import cv2

class ImageGallery:
    def __init__(self, root):
        self.root = root
        self.folder_path = ""
        self.image_files = []
        self.current_index = 0
        self.points = []  # List to store marked points temporarily
        self.groups = []  # List to store groups of points
        self.tmp_labels = []
        self.group_labels = []
        self.auto_save = True

        # Configure objects of drawing
        self.line_thickness = 2
        self.point_radius = 4
        self.text_font = ("arial", 10)

        self.label = tk.Label(root)
        self.label.grid(row=0, column=0, sticky='n')
        self.label.bind("<Button-1>", self.mark_point)
        self.label.bind("<Button-3>", self.remove_group)  # Bind right-click event to remove_point function
        self.label.bind("<Button-2>", self.remove_last_point)
        self.label.bind_all('<d>', self.next_image)
        self.label.bind_all('<a>', self.prev_image)

        self.clear_button = tk.Button(self.root, text="Clear Points", command=self.clear_points, font=self.text_font)
        self.clear_button.grid(row=1, column=0, pady=5)

        self.save_button = tk.Button(self.root, text="Save", command=self.save_points, font=self.text_font)
        self.save_button.grid(row=2, column=0, pady=5)

        self.delete_button = tk.Button(self.root, text="Delete", command=self.delete_image, font=self.text_font)
        self.delete_button.grid(row=3, column=0, pady=5)

        self.coordinate_text = tk.Text(self.root, height=10, width=90, font=self.text_font)
        self.coordinate_text.grid(row=4, column=0, padx=10)

        self.lb = tk.Listbox(self.root, height=10, width=30, font=self.text_font)
        self.lb.grid(row=4, column=1, padx=10, columnspan=3)

        self.show_button = tk.Button(self.root, text="Go", command=self.selected_item, font=self.text_font)
        self.show_button.grid(row=5, column=1)

        self.status_label = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("arial", 14))
        self.status_label.grid(row=5, column=0, columnspan=2, sticky='w', padx=10, pady=5, ipadx=90)

        self.selected_label = tk.StringVar()
        self.label_selected = True  # Flag to track label selection
        self.label_frame = tk.Frame(root)
        self.label_frame.grid(row=0, column=1)
        self.sample_labels = ["0 : 垂直停車格-空", "1 : 垂直停車格-占用",
                              "2 : 水平停車格-空", "3 : 水平停車格-占用",
                              "4 : 斜停車格-空", "5 : 斜停車格-占用"]

        # Create Radiobuttons for label selection
        for i, label in enumerate(self.sample_labels):
            tk.Radiobutton(self.label_frame,
                           text=label,
                           font=self.text_font,
                           variable=self.selected_label,
                           value=i).grid(row=i + 1, column=1, sticky='w')

        self.label_burtton = tk.Button(self.label_frame, text="Save Label", command=self.save_label)

        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, font=("arial", 12))
        self.file_menu.add_command(label="Open folder", command=self.open_folder)
        self.file_menu.add_command(label="Auto save", command=self.auto_save_option)

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="Option", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

    def selected_item(self, event=None):
        for index in self.lb.curselection():
            if 0 <= index < len(self.image_files):
                self.current_index = index
                self.points.clear()
                self.groups.clear()
                self.tmp_labels.clear()
                self.group_labels.clear()
                self.coordinate_text.delete(1.0, tk.END)
                self.show_image()

    def remove_last_point(self, event):
        if len(self.points) > 0:
            do_remove_point = 0
            for group in self.groups:
                if self.points[-1] in group:
                    do_remove_point += 1
            if do_remove_point == 0:
                self.points.pop()
                self.update_image_with_points()

    def save_label(self):
        label = self.selected_label.get()
        if label:
            self.group_labels.append(label)
            self.update_image_with_lines()
            self.display_coordinates()
            self.label_selected = True  # Set label selection flag
            self.label_burtton.grid_forget()
        else:
            messagebox.showerror("Error", "Please select a label.")
            return

    def auto_save_option(self):
        if not self.auto_save:
            self.auto_save = True
            self.status_label.config(
                text=f" Auto save: Enable")
        else:
            self.auto_save = False
            self.status_label.config(
                text=f" Auto save: Disable")

    def open_folder(self):
        self.points.clear()
        self.groups.clear()
        self.tmp_labels.clear()
        self.group_labels.clear()
        self.coordinate_text.delete(1.0, tk.END)
        folder_path = filedialog.askdirectory()
        if folder_path and len(self.image_files) == 0:
            self.folder_path = folder_path
            self.image_files = [f for f in os.listdir(self.folder_path) if
                                os.path.isfile(os.path.join(self.folder_path, f))
                                and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            for idx, file_name in enumerate(self.image_files):
                self.lb.insert("end", " %s" % file_name)
            if self.image_files:
                self.current_index = 0
                self.show_image()

    def show_image(self):
        if self.current_index < len(self.image_files):
            image_path = os.path.join(self.folder_path, self.image_files[self.current_index])

            # Load the image
            img = Image.open(image_path)
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo

            # Check if a JSON file exists for the image
            json_path = os.path.splitext(image_path)[0] + ".json"
            if os.path.exists(json_path):
                with open(json_path, 'r') as json_file:
                    data = json.load(json_file)
                    if "marks" in data and "slots" in data:
                        for group, slot in zip(data["marks"], data["slots"]):
                            group_points = group
                            tmp_points = []
                            for i in range(len(group_points) - 1):
                                self.points.append(tuple(group_points[i]))
                                tmp_points.append(tuple(group_points[i]))

                            self.points.append(tuple(group_points[-1]))
                            tmp_points.append(tuple(group_points[-1]))
                            self.groups.append(tmp_points.copy())
                            self.group_labels.append(slot)

                        self.display_coordinates()

            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo
            self.status_label.config(
                text=f" Image {self.current_index + 1}/{len(self.image_files)}: {self.image_files[self.current_index]}")
            self.update_image_with_lines()

    def next_image(self, event=None):
        if self.current_index < len(self.image_files) - 1:
            if self.auto_save:
                self.save_points()
            self.current_index += 1
            self.points.clear()
            self.groups.clear()
            self.tmp_labels.clear()
            self.group_labels.clear()
            self.coordinate_text.delete(1.0, tk.END)
            self.show_image()
        else:
            messagebox.showerror("Error", "No more images")
            return

    def prev_image(self, event=None):
        if self.current_index > 0:
            if self.auto_save:
                self.save_points()
            self.current_index -= 1
            self.points.clear()
            self.groups.clear()
            self.tmp_labels.clear()
            self.group_labels.clear()
            self.coordinate_text.delete(1.0, tk.END)
            self.show_image()
        else:
            messagebox.showerror("Error", "No more images")
            return

    def chooce_to_show(self):
        if not self.image_files:
            messagebox.showerror("Error", "Open folder load all the images first.")
            return

        image_path = filedialog.askopenfilename(filetypes=[('image files', '*.jpg')])
        image_name = image_path.split("/")[-1]
        if image_name in self.image_files:
            idx = self.image_files.index(image_name)
            self.current_index = idx
            self.points.clear()
            self.groups.clear()
            self.tmp_labels.clear()
            self.group_labels.clear()
            self.coordinate_text.delete(1.0, tk.END)
            self.show_image()
        else:
            if image_name is not "":
                messagebox.showerror("Error", "Wrong folder")
                return

    def mark_point(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))

        if len(self.points) % 4 == 0:  # Check if 4 points have been marked
            if not self.label_selected:
                messagebox.showerror("Error", "Please set a label for the current group before marking new points.")
                self.points = self.points[:-4]  # Remove the last 4 points
                return

            # Store the group of points temporarily
            self.groups.append(self.points[-4:])

            # Clear the text field
            self.coordinate_text.delete(1.0, tk.END)
            self.label_burtton.grid(row=7, column=1)

        self.update_image_with_points()
        # self.update_image_with_lines()

    def remove_group(self, event):
        x, y = event.x, event.y
        for i, group in enumerate(self.groups):
            # Check if click is within the range of any group
            x_values = [point[0] for point in group]
            y_values = [point[1] for point in group]
            min_x, max_x = min(x_values), max(x_values)
            min_y, max_y = min(y_values), max(y_values)
            if min_x <= x <= max_x and min_y <= y <= max_y:
                for point in group:
                    self.points.remove(point)
                self.groups.pop(i)
                self.group_labels.pop(i)
                self.update_image_with_lines()
                self.display_coordinates()
                break

        # Redraw image after removal
        self.update_image_with_lines()

    def update_image_with_lines(self):
        img_path = os.path.join(self.folder_path, self.image_files[self.current_index])
        img = cv2.imread(img_path)
        for idx, group in enumerate(self.groups):
            for i in range(len(group) - 1):
                cv2.line(img, group[i], group[i + 1], (255, 0, 0), self.line_thickness)

            cv2.line(img, group[-1], group[0], (255, 0, 0), self.line_thickness)
            for point in self.points:
                cv2.circle(img, (point[0], point[1]), self.point_radius, (0, 0, 255), -1)
            # for point in group:
            #     cv2.circle(img, (point[0], point[1]), self.point_radius, (0, 0, 255), -1)

            label = self.group_labels[idx]
            x_values = [point[0] for point in group]
            y_values = [point[1] for point in group]
            x_center, y_center = int(sum(x_values) / len(x_values)), int(sum(y_values) / len(y_values))

            cv2.putText(img, str(label), (x_center, y_center), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        1, (0, 255, 255), 1, cv2.LINE_AA)

        pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        photo = ImageTk.PhotoImage(pil_image)
        self.label.config(image=photo)
        self.label.image = photo

    def update_image_with_points(self):
        img_path = os.path.join(self.folder_path, self.image_files[self.current_index])
        img = cv2.imread(img_path)
        for idx, group in enumerate(self.groups):
            if len(group) >= 2:
                for i in range(len(group) - 1):
                    cv2.line(img, group[i], group[i + 1], (255, 0, 0), self.line_thickness)
                cv2.line(img, group[-1], group[0], (255, 0, 0), self.line_thickness)


        for point in self.points:
            cv2.circle(img, (point[0], point[1]), self.point_radius, (0, 0, 255), -1)

        pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        photo = ImageTk.PhotoImage(pil_image)
        self.label.config(image=photo)
        self.label.image = photo

    def clear_points(self):
        self.points.clear()
        self.groups.clear()
        self.group_labels.clear()
        self.coordinate_text.delete(1.0, tk.END)
        self.update_image_with_lines()

    def save_points(self):
        img_filename = self.image_files[self.current_index]
        img_name, img_ext = os.path.splitext(img_filename)
        save_data = {"image_file": img_filename, "marks": self.groups, "slots": self.group_labels}
        save_path = os.path.join(self.folder_path, f"{img_name}.json")
        with open(save_path, "w") as file:
            json.dump(save_data, file)
        self.status_label.config(text=f" Points saved to {save_path}")

    def display_coordinates(self):
        self.coordinate_text.delete(1.0, tk.END)  # Clear previous text
        for i, group in enumerate(self.groups):
            coordinates = ', '.join([f"({point[0]}, {point[1]})" for point in group])
            label = self.group_labels[i] if i < len(self.group_labels) else "No Label"
            self.coordinate_text.insert(tk.END, f"Group {i + 1}: {coordinates} - Label: {label}\n")

    def delete_image(self):
        if self.current_index < len(self.image_files):
            image_path = os.path.join(self.folder_path, self.image_files[self.current_index])
            # Delete the current image file
            if os.path.exists(image_path):
                os.remove(image_path)
                # Delete other files with the same name (e.g., JSON file)
                file_name, file_extension = os.path.splitext(image_path)
                for file in os.listdir(self.folder_path):
                    if file.startswith(os.path.basename(file_name)) and file != os.path.basename(image_path):
                        os.remove(os.path.join(self.folder_path, file))
                self.points.clear()
                self.groups.clear()
                self.tmp_labels.clear()
                self.group_labels.clear()
                self.coordinate_text.delete(1.0, tk.END)
                # Update the image list and show the next image
                self.image_files = [file for file in os.listdir(self.folder_path) if
                                    file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                self.lb.delete(0, 'end')
                for idx, file_name in enumerate(self.image_files):
                    self.lb.insert("end", "%03d %s" % (idx, file_name))
                self.show_image()


# Create the main window
root = tk.Tk()
root.title("Image Viewer")
root.geometry("+700+40")
gallery = ImageGallery(root)

# Run the application
root.mainloop()
