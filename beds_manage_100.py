import streamlit as st
from datetime import datetime, timedelta
import json
import pytz

ROOMS = {
    "B1": {"gender": "Male", "capacity": 3, "occupants": []},
    "B2": {"gender": "Male", "capacity": 3, "occupants": []},
    "B3": {"gender": "Male", "capacity": 3, "occupants": []},
    "B4": {"gender": "Male", "capacity": 3, "occupants": []},
    "B5": {"gender": "Male", "capacity": 3, "occupants": []},
    "B6": {"gender": "Male", "capacity": 3, "occupants": []},
    "B7": {"gender": "Male", "capacity": 3, "occupants": []},
    "B8": {"gender": "Male", "capacity": 3, "occupants": []},
    "B9": {"gender": "Male", "capacity": 3, "occupants": []},
    "B10": {"gender": "Male", "capacity": 3, "occupants": []},
    "B11": {"gender": "Male", "capacity": 3, "occupants": []},
    "B12": {"gender": "Male", "capacity": 12, "occupants": []},
    "B13": {"gender": "Male", "capacity": 3, "occupants": []},
    "B14": {"gender": "Male", "capacity": 3, "occupants": []},
    "B15": {"gender": "Male", "capacity": 3, "occupants": []},
    "B16": {"gender": "Male", "capacity": 3, "occupants": []},
    "B17": {"gender": "Male", "capacity": 12, "occupants": []},
    "B18": {"gender": "Male", "capacity": 3, "occupants": []},
    "B19": {"gender": "Male", "capacity": 3, "occupants": []},
    "B20": {"gender": "Male", "capacity": 3, "occupants": []},
    "B21": {"gender": "Male", "capacity": 12, "occupants": []},
    "B22": {"gender": "Male", "capacity": 3, "occupants": []},
    "B23": {"gender": "Male", "capacity": 3, "occupants": []},
    "B24": {"gender": "Male", "capacity": 3, "occupants": []},
    "D12": {"gender": "Female", "capacity": 12, "occupants": []},
    "D17": {"gender": "Female", "capacity": 12, "occupants": []}
}
# Function to load room data from a JSON file and remove expired occupants
def load_data(remove=None):
    try:
        with open('rooms_data.json', 'r') as file:
            data = json.load(file)

        jerusalem_zone = pytz.timezone('Asia/Jerusalem')
        current_time = datetime.now().astimezone(jerusalem_zone)

        for room in data.values():
            room['occupants'] = [
                occupant for occupant in room['occupants']
                if
                datetime.fromisoformat(occupant['booking_time']) + timedelta(hours=occupant['duration']) > current_time
                and occupant['name'] != remove]


        save_data(data)  # Save updated data back to the file
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return ROOMS


# Function to save room data to a JSON file
def save_data(data):
    with open('rooms_data.json', 'w') as file:
        json.dump(data, file, indent=4)


# Function to check room availability
def check_availability(room, data):
    return len(data[room]['occupants']) < data[room]['capacity']


# Function to convert local time to Jerusalem time
def to_jerusalem_time(local_time):
    jerusalem_zone = pytz.timezone('Asia/Jerusalem')
    return local_time.astimezone(jerusalem_zone)


# Function to book a room
def book_room(name, room, duration, data):
    jerusalem_now = to_jerusalem_time(datetime.now())
    if all(name != occupant['name'] for occupant in data[room]['occupants']):
        data[room]['occupants'].append({
            "name": name,
            "booking_time": jerusalem_now.isoformat(),
            "duration": duration
        })
        save_data(data)
        return True
    return False


# Function to format end time
def format_end_time(booking_time, duration):
    end_time = datetime.fromisoformat(booking_time) + timedelta(hours=duration)
    end_time_jerusalem = to_jerusalem_time(end_time)
    return end_time_jerusalem.strftime("Until %H:%M")


# Function to remove an occupant from a room
def remove_occupant(room, occupant_name, data):
    data[room]['occupants'] = [
        occupant for occupant in data[room]['occupants'] if occupant['name'] != occupant_name
    ]
    save_data(data)


# Initialize session state for removal confirmation
if 'remove_state' not in st.session_state:
    st.session_state['remove_state'] = {}

# Streamlit app starts here
st.title("Beds Booking 100")
rooms = load_data()

# Step 1: Select Gender
gender = st.radio("Select your gender:", ("Male", "Female"))

# Step 2: Room Selection based on Gender
if gender:
    # Filter out full rooms
    available_rooms = {room: details for room, details in rooms.items()
                       if details['gender'].lower() == gender.lower() and check_availability(room, rooms)}

    if available_rooms:
        selected_room = st.selectbox("Choose a room:", list(available_rooms.keys()))

        # Step 3: Show Occupants and Booking Interface
        if selected_room:
            occupants = rooms[selected_room].get('occupants', [])
            occupant_names = [occupant['name'] for occupant in occupants]
            st.write(f"Sleepers in {selected_room}: {', '.join(occupant_names)}")

            with st.form("book_room"):
                name = st.text_input("Enter your name:", "")
                duration = st.select_slider("Duration (hours):", options=list(range(1, 11)), value=10)
                submitted = st.form_submit_button("Book a Bed")
                if submitted:
                    if name and check_availability(selected_room, rooms):
                        if book_room(name, selected_room, duration, rooms):
                            jerusalem_now = to_jerusalem_time(datetime.now())
                            st.success(
                                f"Booked a bed in room {selected_room} for {name} staring at {jerusalem_now.strftime('%H:%M')} for {duration} hours.")
                        else:
                            st.error("Name already exists in the room.")
                    else:
                        st.error("Room is full")
                        st.experimental_rerun()
    else:
        st.write("No rooms available for your selection.")

# Step 4: View All Occupants with Remove Option
remove_clicked = False
if st.button("Show All Sleepers"):
    for room, details in rooms.items():
        st.write(f"{room}:")
        for occupant in details.get('occupants', []):
            end_time_formatted = format_end_time(occupant['booking_time'], occupant['duration'])
            st.write(f"{occupant['name']} - {end_time_formatted}")
        if remove_clicked:
            break
name = st.text_input("Enter Sleeper's name:", "")
if st.button("Remove Sleeper"):
    if '100100' in name:
        load_data(remove=name.replace('100100',""))

