from flask import Blueprint, render_template, request,abort, jsonify, current_app,redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from .models import db, BlogCategory, MyUser, BlogPost, NewsPost
from datetime import datetime


main = Blueprint('main', __name__)

dummy_newsposts = [
    {
       "post_id":1,
        "category":"business",
        "title": "Atlanta airport sees continued delays, cancellations", 
        "author": "Mike W",
        "image":"images/post_img_1.png",
        "date_created": datetime.now(),
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },

    },
    {
        "post_id":2,
        "category":"business",
        "title": "Atlanta's Housing Market Sees Unexpected Surge", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_2.png",
        "date_created": datetime.now()
    },
    {
        "post_id":3,
        "category":"business",
        "title": "5 must-visit coffee shops in Midtown", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_3.png",
        "date_created": datetime.now()
    },
    {
        "post_id":4,
        "category":"business",
        "title": "5 must-visit coffee shops in Midtown", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_1.png",
        "date_created": datetime.now()
    },
    {
        "post_id":5,
        "category":"business",
        "title": "City Council passes new zoning laws", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_2.png",
        "date_created": datetime.now()
    },
    {
        "post_id":6,
        "category":"business",
        "title": "Tech scene expands beyond Buckhead", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_3.png",
        "date_created": datetime.now()
    },
    {
        "post_id":7,
        "category":"business",
        "title": "MARTA unveils new transit plans", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":None,
        "date_created": datetime.now()
    },
    {
        "post_id":8,
        "category":"business",
        "title": "Entrepreneur builds app for Atlanta locals", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_1.png",
        "date_created": datetime.now()
    },
    {
        "post_id":9,
        "category":"business",
        "title": "City Council Approves New Park Plan", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_2.png",
        "date_created": datetime.now()
    },
    {
        "post_id":10,
        "category":"business",
        "title": "Meet the Chef Behind ATL's Hottest New Pop-Up", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_3.png",
        "date_created": datetime.now()
    },
    {
        "post_id":11,
        "category":"business",
        "title": "West End Mural Project Brings History to Life", 
        "author": "Mike W",
        "content":{
            "section-1":{
                "title":"Introduction to Hartsfield-Jackson Atlanta International Airport",
                "paragraph-1":"Hartsfield-Jackson Atlanta International Airport (ATL) isn’t just the busiest airport in the U.S.—it’s one of the most crucial hubs in global air travel. With over 100 million passengers annually, ATL serves as a central connecting point for domestic and international flights, making any disruption at this airport a ripple felt across the nation.",
                "paragraph-2":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
                "paragraph-3":"Home to Delta Air Lines, which manages the lion’s share of arrivals and departures, ATL is experiencing continued delays and cancellations that are frustrating travelers and raising industry concerns.",
            },
            "section-2":{
                "title":"Why Are Flights Being Delayed and Canceled?",
                "paragraph-1":"Flight delays and cancellations aren’t new—but the consistency and volume ATL is facing this year have drawn attention. Multiple overlapping factors are contributing to the persistent chaos.",
                "paragraph-2":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
                "paragraph-3":"Atlanta’s summer weather can be unpredictable. Thunderstorms, fog, and occasional lightning strikes often disrupt takeoffs and landings. Unlike mechanical issues, weather disruptions can cause a chain reaction, grounding planes in other cities and leading to rolling delays throughout the day.",
            },
            "section-3":{
                "title":"Delta Airlines Takes the Brunt of Cancellations",
                "paragraph-1":"As the largest operator at ATL, Delta Airlines has been disproportionately affected.",
                "paragraph-2":"Delta’s extensive network relies heavily on ATL. When delays strike, the domino effect spreads to dozens of connecting flights. Crew scheduling issues, mechanical maintenance, and last-minute aircraft swaps have further compounded the problem.",
                "paragraph-3":"Post-pandemic travel has rebounded with surprising speed. Summer vacations, business conferences, and international travel demand have overwhelmed Delta’s systems, leading to overbooking and logistical strain.",
            },
            "section-4":{
                "title":"How the Disruptions Affect Travelers",
                "paragraph-1":"Flight cancellations often mean unplanned hotel stays, expensive rebookings, and missed prepaid plans. Although some travel insurance policies cover these costs, not everyone is covered—or reimbursed fully.",
                "paragraph-2":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
                "paragraph-3":"Business travelers and international tourists are particularly vulnerable. Missed meetings, rescheduled layovers, and limited rebooking options are hurting confidence in using ATL as a reliable hub.",
            },
            "section-5":{
                "title":"What Is Being Done to Fix the Problem?",
                "paragraph-1":"Delta has begun hiring additional crew, investing in fleet maintenance, and offering more real-time updates through its mobile app. The airline is also proactively canceling lower-demand flights in advance to avoid last-minute chaos.",
                "paragraph-2":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
                "paragraph-3":"The FAA has acknowledged the staffing issues and launched accelerated training programs. Meanwhile, ATL is working with federal and state officials to secure funding for additional gates and smoother passenger flow enhancements.",
            },
            "section-6-conclusion":{
                "title":"Flying Through the Chaos with Confidence",
                "paragraph-1":"Travelers passing through ATL are facing an increasingly uncertain experience. Yet, understanding the root causes and being prepared can make a major difference. Whether you're flying for business or leisure, a little planning—and a lot of patience—can help you navigate the current turbulence at Hartsfield-Jackson Atlanta International Airport.",
                "paragraph-2":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
                "paragraph-3":"Stay informed, arrive early, and use the right tools. With time, operational improvements and infrastructure upgrades may bring smoother skies to ATL’s millions of passengers.",
            },
            "section-7-assoc-press":{
                "title":"The Atlanta Local",
                "paragraph-1":"Copyright 2025 The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed without permission.",
            },
            "sectition-8-faqs":[
                {
                    "question":"Why is Delta most affected by ATL delays?", 
                     "answer":"As the main airline operating at ATL, Delta’s extensive schedule is deeply tied to ATL’s functioning. A disruption here affects Delta's entire network.",
                 },
                    {
                    "question":"Is it better to fly out of a different airport nearby?", 
                     "answer":"Sometimes. Nearby airports like Birmingham or Charlotte may offer alternatives, but not all destinations are available.",
                 },
                {
                    "question":"How can I get compensation for canceled flights?", 
                     "answer":"Check Delta’s cancellation policy and the Department of Transportation’s refund rules. You may be eligible for vouchers or refunds.",
                 },

                {
                    "question":"Does ATL have enough infrastructure to handle its current traffic?", 
                     "answer":"The airport is working on expanding, but current facilities are stretched thin during peak hours.",
                 },

                {
                    "question":"Can travel insurance help in these situations?", 
                     "answer":"Yes, if you have coverage for delays or cancellations. Always check the fine print before traveling.",
                 },
                {
                    "question":"Is this situation unique to Atlanta?", 
                     "answer":"No, but ATL’s size amplifies its challenges. Other major hubs like JFK and LAX face similar issues.",
                 },
            ],
        },
        "image":"images/post_img_1.png",
        "date_created": datetime.now()
    },

]


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        # Adjust this line to match your model:
        #   - If you have a boolean: current_user.is_admin
        #   - If you have a role string: current_user.role == "admin"
        is_admin = getattr(current_user, "is_admin", False) or getattr(current_user, "role", "") == "admin"

        if not is_admin:
            # Choose one behavior; redirect with flash or 403.
            flash("You do not have permission to access that page.", "error")
            return redirect(url_for("main.home"))
            # Or: abort(403)

        return view_func(*args, **kwargs)
    return wrapped

@main.route("/")
@main.route("/home")
def home():
    return render_template("search_map/search_home.html")

# News -> "/news" (kept as its own endpoint)
@main.route("/news")
def news():
    return render_template("news/index.html")

@main.route('/news/<int:news_id>')
def news_detail(news_id):

    return render_template('news/news_detail.html')

@main.route('/blog')
def blog():
    return render_template('blog/index.html')

@main.route('/companies')
def company_home():
    return render_template('company_profile/company_profile_listview.html')


@main.route('/companies/<int:company_id>')
def company_detail(company_id):

    return render_template('company_profile/compay_profile_detailview.html')

@main.route('/blog/<int:post_id>')
def blog_detail(post_id):

    return render_template('blog/blog_detail.html')


@main.route('/about')
def about():
    return render_template('home/about.html')

@main.route('/search-map')
def search_map():
    return render_template('search_map/search_home.html')

@main.route('/directory')
def directory():
    news = [
        {
            "title": "Teaz Social Expands with More Live Events",
            "summary": "Atlanta's favorite social tea lounge is now hosting weekly open mic nights, live DJs, and community mixers.",
            "image": "/story_tea.png"
        },
        {
            "title": "Mike Launches the ATL Local App",
            "summary": "Founder Mike officially launches ATL Local, a new community-driven search engine built for Atlantans by Atlantans.",
            "image": "/story_mike_atl_local.png"
        }
    ]
    weather = {
        "icon": "/static/images/weather-sun.png",
        "temperature": "87°F",
        "condition": "Sunny",
        "location": "Atlanta, GA"
    }
    return render_template('home/index.html', news=news, weather=weather)



@main.route('/shop')
def shop():
    JOIN_URL = 'https://www.paypal.com/ncp/payment/39WCXLXMZWSCY'
    return render_template('shop/index.html', join_url = JOIN_URL)

@main.route('/book')
def book():
    return render_template('book/index.html')

@main.route('/digital-products')
def digital_products():
    return render_template('digital_products/index.html')

@main.route('/events')
def events():
    return render_template('events/index.html')

@main.route('/real-estate')
def real_estate():
    return render_template('real_estate/index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        email      = request.form.get('email')
        password   = request.form.get('password')
        confirm    = request.form.get('confirm_password')
        gender     = (request.form.get('gender') or "").strip().lower()
        dob        = request.form.get('dob')
        zip_code   = request.form.get('zip_code')
        city_state = request.form.get('city_state')
        image      = request.form.get('image')  # simple string path for now

        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect(url_for('main.register'))

        existing_user = MyUser.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered", "error")
            return redirect(url_for('main.register'))

        # normalize gender to match DB constraint
        if gender == "prefer-not-to-say":
            gender = "na"
        allowed = {"male", "female", "non-binary", "other", "na"}
        if gender not in allowed:
            flash("Select a valid gender option.", "error")
            return redirect(url_for('main.register'))

        hashed_pw = generate_password_hash(password)

        new_user = MyUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=hashed_pw,
            gender=gender,
            dob=dob,
            zip_code=zip_code,
            city_state=city_state,
            image=image or ""
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('main.login'))

    return render_template('admin/register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        user = MyUser.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password", "error")
            return redirect(url_for('main.login'))

        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect(url_for('main.admin_home'))

    return render_template('admin/login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('main.login'))


@main.route('/admin')
@admin_required
def admin_home():
    return render_template('admin/index.html')

@main.route('/admin/users',methods=['GET',])
@admin_required
def admin_users():
    return render_template('admin/user_list_view.html')

@main.route('/admin/blog-cat',methods=['GET',])
@admin_required
def admin_blog_cats():
    return render_template('admin/blog_cat_list_view.html')

@main.route('/admin/blog',methods=['GET',])
@admin_required
def admin_blog_post():
    return render_template('admin/blog_list_view.html')


@main.route('/admin/blog/create',methods=['GET', 'POST'])
@admin_required
def admin_create_blog_post():
    return render_template('admin/create_post.html')

@main.route('/admin/blogs/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def admin_blog_detail(post_id):
    return render_template('admin/read_update_post.html')


@main.route('/admin/news',methods=['GET',])
@admin_required
def admin_news_post():
    return render_template('admin/news_list_view.html')

@main.route('/api/debug/db')
@admin_required
def debug_db():
    # Counts
    cat_count  = BlogCategory.query.count()
    user_count = MyUser.query.count()
    post_count = BlogPost.query.count()
    news_count = NewsPost.query.count()

    # Log a few rows to the server console
    print("\n--- DB DEBUG ---")
    print(f"BlogCategory count: {cat_count}")
    for c in BlogCategory.query.order_by(BlogCategory.blog_cat_id).limit(3):
        print(f"  - [{c.blog_cat_id}] {c.title} (slug={c.slug})")

    print(f"MyUser count: {user_count}")
    for u in MyUser.query.order_by(MyUser.my_user_id).limit(3):
        print(f"  - [{u.my_user_id}] {u.first_name} {u.last_name} <{u.email}>")

    print(f"BlogPost count: {post_count}")
    for p in BlogPost.query.order_by(BlogPost.post_id).limit(3):
        print(f"  - [{p.post_id}] {p.title} (slug={p.slug}) cat_id={p.blog_cat_id} author_id={p.author_id}")

    print(f"NewsPost count: {news_count}")
    for n in NewsPost.query.order_by(NewsPost.post_id).limit(3):
        print(f"  - news post_id={n.post_id}")
    print("--- END DB DEBUG ---\n")

    # Also return a small JSON so you can check in the browser
    return jsonify({
        "blog_category_count": cat_count,
        "my_user_count": user_count,
        "blog_post_count": post_count,
        "news_post_count": news_count
    })



