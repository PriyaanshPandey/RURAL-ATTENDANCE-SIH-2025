# RURAL-ATTENDANCE-SIH-2025


## 💡 The Problem
**Manual student attendance** is a significant challenge, especially in rural schools. It is prone to errors, wastes valuable class time , and is susceptible to proxy attendance. Furthermore, traditional electronic systems are often too expensive and rely on reliable internet, which is not always available in rural regions.




## 🌟 Our Solution: Fast, Reliable, and Affordable
We developed a 

**cost-effective and simple** , **web-based Progressive Web App** (PWA) to empower teachers to efficiently and accurately mark student attendance. Our system addresses the core challenges by providing a robust 


**QR code-based solution** that functions both online and **offline** .

This system is designed to save up to 

**82% of time** and **cut costs by 90%** compared to expensive hardware systems.


## ✨ Key Features 

1.  **Attendance Marking**
The platform offers a versatile approach to marking attendance, ensuring reliability even with internet issues.




**Primary Method** : QR Code Scanning: Teachers can quickly mark attendance by scanning a student's unique QR code. (See technical approach for flow) 




**Secondary Method** : Manual Entry: A manual attendance feature is available as a fallback in case QR entry fails or for daily use, allowing teachers to mark students as Present or Absent with a single click.


**Bulk Actions** : Features like "Mark All Present" and "Mark All Absent" simplify the process further. 



   

2. **Management and Reports**
   
The system includes an Admin Dashboard for easy management and data visualization.


**Class & Student Management** : Easily add new classes and manage student records, including Roll Numbers, Names, and associated QR Codes.

 **Attendance Reports:** Generate daily, weekly, or custom-date-range reports showing the total number of **Present** and **Absent** students for a selected class. The reports are generated instantly for transparent records. 
 
3.**Usability and Accessibility**
The design focuses on ease of use for non-technical users and regional compatibility.


**PWA Architecture**: As a Progressive Web App, it offers a native app-like experience on the web, enabling offline mode.


**Offline Functionality**: Can work even without an internet connection in rural regions. Data is temporarily stored locally and synced later when online.


**Multilingual Support**: Available in English, Hindi, and Punjabi to cater to diverse rural populations.



## ⚙️ Technical Approach
Our system architecture is a Progressive Web App (PWA) designed for an offline-first experience, ensuring operational feasibility even with intermittent internet access.





**Architecture Flow**

**Teacher Access** : The teacher logs in via the PWA on their smartphone or tablet. 


**Attendance** : They choose the "Take Attendance" view. 


**Online Mode** : QR scan data is immediately sent to the Attendance database via the network. 



**Offline Mode** : If the network is unavailable, the QR scan data is stored temporarily in IndexedDB (client-side storage). 


**Synchronization** : Once the device connects to the internet, the data from IndexedDB is automatically synced to the central Attendance database. 



**Reporting** : The "See Attendance" view and report generation process retrieve data from the main database via a Flask API, enabling data visualization and report generation. 


## Core Technologies

### Frontend: Progressive Web App (PWA) 



### Offline Storage: IndexedDB (for local, temporary storage) 


### Backend API: Flask API (for handling report generation and database interactions) 

### Database: Central Attendance Database

### Addressing Challenges
We designed specific solutions for common risks: 

Challenge	Solution 

1. Unreliable Internet	
Use offline data storage (IndexedDB) and sync when online.



2. Expensive Hardware	
Use teachers’ existing smartphones/tablets for scanning (minimal infrastructure).




3. Proxy Attendance	
Implement teacher approval for the QR scan to verify the student's presence.


5. Technical Training	
Conduct short, targeted training sessions for teachers and students.



## 📈 Future Scope
We plan to enhance the system with advanced features:


Analytics Dashboard: Implement a comprehensive dashboard for deeper data insights.


SMS Notifications: Automatically send notifications to parents about student absentees to improve accountability.



Expand Functionality: Integrate other related attendance features (e.g., leave applications, shift attendance).
