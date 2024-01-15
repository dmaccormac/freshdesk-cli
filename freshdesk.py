
# Program: Fresdesk.py
# Description: Provides basic command-line access to freshdesk. View, reply or close tickets.
# Author: Dan MacCormac
# Date: 2019-07-12
# Notes: Requires requests module: http://docs.python-requests.org/


# Imports
import requests
import json
import getpass
from os import system, name


# Config variables
api_key = "your-api-key"
domain = "your-domain"
password = "your-password"
# my tickets, new tickets:
request_url = ("https://" + domain +
               ".freshdesk.com/api/v2/tickets?filter=new_and_my_open&include=requester")
# all tickets, any status:
# request_url = ("https://"+ domain +".freshdesk.com/api/v2/tickets?include=requester")


# Clears the console screen
def clear_console():

    # Windows
    if name == 'nt':
        _ = system('cls')

    # Mac/Linux (os.name is 'posix')
    else:
        _ = system('clear')


# Function: show_tickets()
# Description: Display list of tickets in table-like format.
# By default - shows only tickets assigned to you as well as new tickets.
# To view all tickets - see request_url variable in 'Config variables' section
def show_tickets():

    print("-------------------------------------------------------------------------------------------------")
    print("											https://" + domain + ".freshdesk.com/")
    print("-------------------------------------------------------------------------------------------------")

    # build request object
    r = requests.get(request_url, auth=(api_key, password))

    # success
    if r.status_code == 200:
        tickets = (json.loads(r.content))
        print("ID\tStatus\tCreated\t\t\tCreator\t\t\tSubject")  # header columns
        for t in tickets:
            print(t["id"], "\t", t["status"], "\t", t['created_at'], t["requester"]
                  ["name"], "\t", t["subject"])  # individual ticket attributes

    # fail
    else:
        print("Failed to read tickets, errors are displayed below,")
        response = json.loads(r.content)
        print(response["errors"])
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))


# Function: view_ticket()
# Description: Diplays an individual ticket including converstations/replies.
# Parameters:
# ticket_id - string represeting ticket id number
def view_ticket(ticket_id):

    # build request
    r = requests.get("https://" + domain + ".freshdesk.com/api/v2/tickets/" +
                     ticket_id + "?include=requester,conversations", auth=(api_key, password))

    # success
    if r.status_code == 200:
        t = (json.loads(r.content))  # get ticket content

        # retrieve fields/data from ticket object t
        tckt = (t["requester"]["email"])
        tckt += '\n' + (t["created_at"])
        tckt += '\n' + (t["description_text"])
        for item in t['conversations']:
            # tckt += '\n\n' + (item['from_email'])
            tckt += '\n' + (item['created_at'])
            tckt += "\n" + (item['body_text'])

    # fail
    else:
        print("Failed to read ticket, errors are displayed below,")
        response = json.loads(r.content)
        print(response["errors"])

    return tckt


# Function: add_reply()
# Description: Adds a reply to a ticket
# Parameters:
# ticket_id - string; the id number of the ticket
# message - string; the text reply to add to the ticket
def add_reply(ticket_id, message):
    headers = {'Content-Type': 'application/json'}

    note = {
        'body': message
    }

    r = requests.post("https://" + domain + ".freshdesk.com/api/v2/tickets/"+ticket_id +
                      "/reply", auth=(api_key, password), headers=headers, data=json.dumps(note))

    if r.status_code == 201:
        print("Reply added successfully, the response is given below")
        print(r.content)
        print("Location Header: " + r.headers['Location'])
    else:
        print("Failed to add reply, errors are displayed below,")
        response = json.loads(r.content)
        print(response["errors"])

        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))


def update_ticket(ticket_id, status):
    headers = {'Content-Type': 'application/json'}

    ticket = {
        'status': int(status),
    }

    r = requests.put("https://" + domain + ".freshdesk.com/api/v2/tickets/"+ticket_id,
                     auth=(api_key, password), headers=headers, data=json.dumps(ticket))

    if r.status_code == 200:
        print("Ticket updated successfully.")
        input("ENTER to continue")
    else:
        print("Failed to update ticket, errors are displayed below,")
        response = json.loads(r.content)
        print(response["errors"])

        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + r.status_code)


# Function: show_dashboard()
# Description: Shows the dashboard with list of tickets. enter ticket id to view that ticket.
# Arugments: none
def show_dashboard():
    # show ticket list and 'id?' prompt
    show_tickets()
    ticket_id = input("\nid? ")

    # show individual ticket requested
    clear_console()
    print("Ticket #", ticket_id)
    print(view_ticket(ticket_id))

    # show menu options: reply, status, back
    i = input("\n[r]eply			[s]tatus		[b]ack 	:")
    if i == "r":
        message = input("message: ")
        add_reply(ticket_id, message)
    elif i == "s":
        status = input("2=open, 3=pending, 4=resolved, 5=close. status?")
        update_ticket(ticket_id, status)
    elif i == "b":
        return


# main
while True:
    clear_console()
    show_dashboard()
