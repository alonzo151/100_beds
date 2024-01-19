import streamlit as st
from datetime import datetime, timedelta
import json
import pytz

BEDS_BARCKS = {
    "Nofit4": {"gender": "Male", "capacity": 4, "occupants": []},
    "Nofit6": {"gender": "Male", "capacity": 4, "occupants": []},
    "Carmel8": {"gender": "Male", "capacity": 5, "occupants": []},
    "Carmel9": {"gender": "Male", "capacity": 5, "occupants": []},
    "Carmel10": {"gender": "Male", "capacity": 5, "occupants": []},
    "Carmel11": {"gender": "Male", "capacity": 5, "occupants": []},
    "Carmel12": {"gender": "Male", "capacity": 5, "occupants": []},
    "Carmel13": {"gender": "Male", "capacity": 5, "occupants": []},
    "Carmel14": {"gender": "Male", "capacity": 5, "occupants": []},
    "Carmel15": {"gender": "Male", "capacity": 5, "occupants": []},
    "BOQ3": {"gender": "Male", "capacity": 4, "occupants": []},
    "BOQ6": {"gender": "Male", "capacity": 3, "occupants": []},
    "BOQ11": {"gender": "Male", "capacity": 4, "occupants": []},
    "BOQ12": {"gender": "Female", "capacity": 4, "occupants": []}
}
BOQ_ROOM = {

}

beds_pass = "100100"
boq_pass = "100boq"

# Create an input field for the password
user_password = st.text_input("Enter the password:", type="password")

# Check if the entered password matches the correct password
if user_password in [beds_pass, boq_pass]:

    if user_password == "100100":
        json_file = 'rooms_data.json'
        sleep_resource = BEDS_BARCKS

    if user_password == "100boq":
        json_file = 'boq_data.json'
        sleep_resource = BOQ_ROOM

    st.success("Password accepted. You can access the app.")


    # Function to load room data from a JSON file and remove expired occupants
    def load_data(remove=None):
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)

            jerusalem_zone = pytz.timezone('Asia/Jerusalem')
            current_time = datetime.now().astimezone(jerusalem_zone)

            for room in data.values():
                room['occupants'] = [
                    occupant for occupant in room['occupants']
                    if
                    datetime.fromisoformat(occupant['booking_time']) + timedelta(
                        hours=occupant['duration']) > current_time
                    and occupant['name'] != remove]

            save_data(data)  # Save updated data back to the file
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return sleep_resource


    # Function to save room data to a JSON file
    def save_data(data):
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)


    # Function to check room availability
    def check_availability(room, data):
        return len(data[room]['occupants']) < data[room]['capacity']


    # Function to convert local time to Jerusalem time
    def to_jerusalem_time(local_time):
        jerusalem_zone = pytz.timezone('Asia/Jerusalem')
        return local_time.astimezone(jerusalem_zone)


    # Function to book a room
    def book_room(name, selected_room, duration, data):
        jerusalem_now = to_jerusalem_time(datetime.now())
        for room in data.keys():
            if any(name == occupant['name'] for occupant in data[room]['occupants']):
                return False  # Name already exists in one of the rooms

        # If name doesn't exist in any room, add it to the first available room

        if check_availability(selected_room, data):
            data[selected_room]['occupants'].append({
                "name": name,
                "booking_time": jerusalem_now.isoformat(),
                "duration": duration
            })
            save_data(data)
            return True  # Successfully booked a bed in the first available room

        return False  # All rooms are full


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
            text = [r + " (" + str(
                available_rooms[r]['capacity'] - len(available_rooms[r]['occupants'])) + " free beds out of " + str(
                available_rooms[r]['capacity']) + ")" for r in available_rooms]
            selected_room = st.selectbox("Choose a room:", text)

            # Step 3: Show Occupants and Booking Interface
            if selected_room:
                selected_room = selected_room.split()[0]
                occupants = rooms[selected_room].get('occupants', [])

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
                                st.error("Name already exists")
                        else:
                            st.error("Room is full")
                            st.experimental_rerun()
                occupant_names = [occupant['name'] for occupant in occupants]
                text = f"Sleepers in {selected_room}: {', '.join(occupant_names)}" if occupant_names else f"Room {selected_room} is currently empy"
                st.write(text)
        else:
            st.write("No rooms available for your selection.")

    # Step 4: View All Occupants with Remove Option
    remove_clicked = False
    hide_all = False
    if st.button("Show All Sleepers"):
        if st.button("Hide All Sleepers"):
            hide_all = True
            pass
        for room, details in rooms.items():
            st.write(f"{room}:")
            for occupant in details.get('occupants', []):
                end_time_formatted = format_end_time(occupant['booking_time'], occupant['duration'])
                st.write(f"{occupant['name']} - {end_time_formatted}")
            if remove_clicked:
                break
            if hide_all:
                break
        if st.button("Hide All Sleepers."):
            hide_all = True
            pass
    name = st.text_input("Enter Sleeper's name:", "")
    if st.button("Remove Sleeper"):
        load_data(remove=name)

else:
    st.error("Incorrect password. Access denied.")
