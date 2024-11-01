import os
import threading
import tkinter as tk  # Import tkinter for Listbox
from tkinter import filedialog

import requests
import ttkbootstrap as ttk

from anime_scrapper import scrapper as anime_scrapper


class AnitakuAnimeDownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Progress Bar Example")

        # Load download location from file or set default
        self.download_location_file = "download_location.txt"
        self.default_download_location = self.load_download_location()

        # Create frames
        self.form_frame = ttk.Frame(self.root)
        self.form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.lists_frame = ttk.Frame(self.root)
        self.lists_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        # Input fields
        self.anime_name_entry = self.create_label_entry(self.form_frame, "Anime Name:")
        self.season_entry = self.create_label_entry(self.form_frame, "Season:")
        self.episode_entry = self.create_label_entry(self.form_frame, "Episode:")

        # Progress meter
        self.meter = ttk.Meter(
            self.progress_frame,
            metersize=200,
            padding=10,
            amountused=0,
            metertype="semi",
            subtext="",
            interactive=False,
            stripethickness=4,
            textright="%",
            bootstyle="info"
        )
        self.meter.pack(pady=20)

        # Submit button
        self.submit_button = ttk.Button(self.form_frame, text="Submit", command=self.submit_form)
        self.submit_button.pack(pady=10)

        # Select download folder button
        self.select_folder_button = ttk.Button(self.form_frame, text="Select Download Folder",
                                               command=self.select_download_folder)
        self.select_folder_button.pack(pady=10)

        # Start download button
        self.start_download_button = ttk.Button(self.form_frame, text="Start Download", command=self.start_download)
        self.start_download_button.pack(pady=10)

        # Add labels for the list boxes
        self.episodes_label = ttk.Label(self.lists_frame, text="Episodes List")
        self.episodes_label.grid(row=0, column=0, padx=10, pady=(10, 0))

        self.queue_label = ttk.Label(self.lists_frame, text="Queue List")
        self.queue_label.grid(row=0, column=1, padx=10, pady=(10, 0))

        self.download_completed_label = ttk.Label(self.lists_frame, text="Download Completed List")
        self.download_completed_label.grid(row=0, column=2, padx=10, pady=(10, 0))

        # Episodes list
        self.episodes_listbox = tk.Listbox(self.lists_frame, width=40, height=10)  # Listbox to display episodes
        self.episodes_listbox.grid(row=1, column=0, padx=10, pady=(0, 10))
        self.episodes_listbox.bind("<<ListboxSelect>>", self.on_episode_select)  # Bind click event

        # Queue list
        self.queue = []
        self.queue_listbox = tk.Listbox(self.lists_frame, width=40, height=10)  # Use tkinter Listbox
        self.queue_listbox.grid(row=1, column=1, padx=10, pady=(0, 10))
        self.queue_listbox.bind("<<ListboxSelect>>", self.on_queue_select)  # Bind click event

        # Download Completed List
        self.download_completed_listbox = tk.Listbox(self.lists_frame, width=40, height=10)  # Use tkinter Listbox
        self.download_completed_listbox.grid(row=1, column=2, padx=10, pady=(0, 10))

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", bootstyle="info")
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="we", padx=20, pady=10)

    def create_label_entry(self, frame, text):
        ttk.Label(frame, text=text).pack(pady=5)
        entry = ttk.Entry(frame, bootstyle="primary", width=30)
        entry.pack(pady=5)
        return entry

    def update_status(self, message):
        self.status_bar.config(text=message)

    def submit_form(self):
        self.update_status("Fetching total episodes...")

        def fetch_total_episodes():
            episode_link = self.episode_entry.get()
            total_episodes = anime_scrapper.get_total_episodes(episode_link)
            self.meter.configure(subtext=f"Total Episodes: {total_episodes}")
            self.populate_episodes_listbox(total_episodes)  # Populate episodes listbox
            self.update_status("Total episodes fetched")

        # Show loading indicator
        self.meter.configure(subtext="Loading...")

        # Run the fetch_total_episodes function in a separate thread
        threading.Thread(target=fetch_total_episodes).start()

    def populate_episodes_listbox(self, total_episodes):
        self.episodes_listbox.delete(0, 'end')
        for episode_num in range(1, total_episodes + 1):
            self.episodes_listbox.insert('end', f"Episode {episode_num}")

    def add_to_queue(self, episode_number):
        if episode_number not in self.queue:
            self.queue.append(episode_number)
            self.queue.sort()  # Ensure the queue is in order
            self.update_queue_listbox()

    def update_queue_listbox(self):
        self.queue_listbox.delete(0, 'end')
        for episode in self.queue:
            self.queue_listbox.insert('end', f"Episode {episode}")

    def on_episode_select(self, event):
        selected_index = self.episodes_listbox.curselection()
        if selected_index:
            selected_episode = self.episodes_listbox.get(selected_index)
            episode_number = int(selected_episode.split()[1])
            self.add_to_queue(episode_number)
            self.episodes_listbox.delete(selected_index)
            self.update_status(f"Episode {episode_number} added to queue")

    def on_queue_select(self, event):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            selected_episode = self.queue_listbox.get(selected_index)
            episode_number = int(selected_episode.split()[1])
            self.queue.remove(episode_number)
            self.update_queue_listbox()
            self.update_status(f"Episode {episode_number} removed from queue")

            # Insert the episode back to the main list in order
            episodes = [int(self.episodes_listbox.get(i).split()[1]) for i in range(self.episodes_listbox.size())]
            episodes.append(episode_number)
            episodes.sort()

            self.episodes_listbox.delete(0, 'end')
            for episode in episodes:
                self.episodes_listbox.insert('end', f"Episode {episode}")

    def select_download_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.default_download_location)
        if folder_selected:
            self.default_download_location = folder_selected
            self.save_download_location(folder_selected)
            self.update_status(f"Download folder set to: {self.default_download_location}")

    def save_download_location(self, folder_path):
        with open(self.download_location_file, 'w') as file:
            file.write(folder_path)

    def load_download_location(self):
        if os.path.exists(self.download_location_file):
            with open(self.download_location_file, 'r') as file:
                return file.read().strip()
        else:
            default_location = os.path.join(os.path.expanduser("~"), "Desktop", "anitaku")
            os.makedirs(default_location, exist_ok=True)
            return default_location

    def start_download(self):
        if not self.queue:
            self.update_status("Queue is empty")
            return

        def download_episode(episode_number):
            anime_url = self.episode_entry.get()
            episode_link = anime_scrapper.construct_episode_link(episode_number, anime_url)
            download_link = anime_scrapper.get_episode_download_link(episode_link)

            if not download_link:
                self.update_status(f"Failed to get download link for Episode {episode_number}")
                return

            response = requests.get(download_link, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024  # 1 Megabyte
            progress = 0
            last_percentage = -1

            download_path = os.path.join(self.default_download_location, f"Episode_{episode_number}.mp4")
            with open(download_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress += len(data)
                    file.write(data)
                    percentage = int((progress / total_size) * 100)
                    if percentage != last_percentage:
                        last_percentage = percentage
                        downloaded_mb = progress // (1024 * 1024)
                        total_mb = total_size // (1024 * 1024)
                        self.meter.configure(amountused=percentage, subtext=f"{downloaded_mb:.2f}MB/{total_mb:.2f}MB")

            self.update_status(f"Episode {episode_number} downloaded")
            self.download_completed_listbox.insert('end', f"Episode {episode_number}")

        def download_all_episodes():
            while self.queue:
                episode_number = self.queue.pop(0)
                self.update_queue_listbox()
                self.update_status(f"Downloading Episode {episode_number}...")
                download_episode(episode_number)

        threading.Thread(target=download_all_episodes).start()


if __name__ == "__main__":
    app = ttk.Window()
    progress_app = AnitakuAnimeDownloaderUI(app)
    app.mainloop()
