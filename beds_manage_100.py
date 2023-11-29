import streamlit as st
import json
import os
import time
import datetime
import pytz

# File to store data
data_file = 'rooms_data.json'

# Function to load room data from file
def load_room_data():
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            return json.load(file)
    else:
        return {
            'Barracks 1 (Boys)': {'beds': 4, 'occupants': []},
            'Barracks 2 (Boys)': {'beds': 4, 'occupants': []},
            'Barracks 3 (Boys)': {'beds': 4, 'occupants': []},
            'Barracks 4 (Boys)': {'beds': 4, 'occupants': []},
            'Barracks 5 (Girls)': {'beds': 6, 'occupants': []},
        }

# Function to save room data to file
def save_room_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file)

# Load data at start
rooms = load_room_data()

def is_name_unique_in_room(room_name, name):
    occupant_names = [occupant['name'].lower() for occupant in rooms[room_name]['occupants']]
    return name.lower() not in occupant_names

def update_occupancy(room_name, new_guest):
    current_time = time.time()
    if len(rooms[room_name]['occupants']) < rooms[room_name]['beds']:
        if is_name_unique_in_room(room_name, new_guest):
            rooms[room_name]['occupants'].append({'name': new_guest, 'time': current_time})
            save_room_data(rooms)  # Save updated data
            return True
        else:
            st.error("Guest with the same name already exists in this room.")
            return False
    else:
        return False

def remove_occupant(room_name, occupant_index):
    rooms[room_name]['occupants'].pop(occupant_index)
    save_room_data(rooms)

def remove_old_occupants():
    current_time = time.time()
    for room_name, room_info in rooms.items():
        room_info['occupants'] = [occupant for occupant in room_info['occupants'] if current_time - occupant['time'] < 120]
    save_room_data(rooms)

def format_time(timestamp):
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    return datetime.datetime.fromtimestamp(timestamp, jerusalem_tz).strftime('%Y-%m-%d %H:%M:%S')

st.title("Guest House Bed Management")

remove_old_occupants()  # Check and remove old occupants

# Display and update rooms
for room_name, room_info in rooms.items():
    occupancy = len(room_info['occupants'])
    st.write(f"**{room_name}** - Occupancy: {occupancy}/{room_info['beds']}")

    new_guest = st.text_input(f"Enter guest name for {room_name}", key=f'input_{room_name}')
    if st.button('Insert', key=f'button_insert_{room_name}'):
        success = update_occupancy(room_name, new_guest)
        if success:
            st.experimental_rerun()
        else:
            st.error("Room is full")

    st.write("Current Occupants:")
    for idx, occupant in enumerate(room_info['occupants']):
        col1, col2 = st.columns([0.8, 0.2])
        formatted_time = format_time(occupant['time'])
        with col1:
            st.write(f"{occupant['name']} - Inserted at: {formatted_time}")

        with col2:
            if st.button('Remove', key=f'button_remove_{idx}_{room_name}'):
                password = st.text_input("Enter password to remove", type="password", key=f'password_{idx}_{room_name}')
                if password and password == "camel100":
                    remove_occupant(room_name, idx)
                    st.experimental_rerun()
                elif password:
                    st.error("Incorrect password")

    st.write("---")
