import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Dashboard.css";

const Dashboard = () => {
  const [timesheets, setTimesheets] = useState([]);
  const [username, setUsername] = useState(""); // ✅ Store username
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedTimesheet, setSelectedTimesheet] = useState(null); // ✅ Store selected timesheet for modal
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          setError("User not authenticated. Please log in.");
          setLoading(false);
          return;
        }

        // ✅ Fetch the logged-in user's details
        const userResponse = await axios.get("http://127.0.0.1:5000/user", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUsername(userResponse.data.username);

        // ✅ Fetch timesheets
        const response = await axios.get("http://127.0.0.1:5000/timesheets", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.length === 0) {
          setError("No timesheets found. Please create a new timesheet.");
        } else {
          setTimesheets(response.data);
        }
      } catch (err) {
        console.error("Error fetching data:", err.response ? err.response.data : err.message);
        setError("Failed to load data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  // ✅ Function to handle logout
  const handleLogout = () => {
    localStorage.removeItem("token"); // Remove token
    navigate("/"); // Redirect to login page
  };

  // ✅ Function to request PDF generation
  const generatePDF = async (timesheetId) => {
    const token = localStorage.getItem("token");

    try {
      const response = await axios.get(`http://127.0.0.1:5000/generate_pdf/${timesheetId}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `timesheet_${timesheetId}.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error generating PDF:", error.response ? error.response.data : error.message);
      alert("Failed to generate PDF. Please try again.");
    }
  };

  // ✅ Function to delete a timesheet
  const deleteTimesheet = async (timesheetId) => {
    const token = localStorage.getItem("token");

    try {
      await axios.delete(`http://127.0.0.1:5000/delete_timesheet/${timesheetId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setTimesheets(timesheets.filter((ts) => ts.id !== timesheetId));
    } catch (error) {
      console.error("Error deleting timesheet:", error.response ? error.response.data : error.message);
      alert("Failed to delete timesheet. Please try again.");
    }
  };

  // ✅ Function to open the modal with the selected timesheet
  const viewReport = (timesheet) => {
    setSelectedTimesheet(timesheet);
  };

  // ✅ Function to close the modal
  const closeModal = () => {
    setSelectedTimesheet(null);
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <span className="username">Welcome, {username}!</span>
        <div className="header-buttons">
          <button className="create-button" onClick={() => navigate("/submit-timesheet")}>
            + Create New Timesheet
          </button>
          <button className="logout-button" onClick={handleLogout}>Logout</button> {/* ✅ Logout button */}
        </div>
      </div>

      {loading ? (
        <p>Loading timesheets...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : (
        <div className="timesheet-list">
          {timesheets.map((ts) => (
            <div key={ts.id} className="timesheet-row">
              <span className="timesheet-title">{ts.project_name} <small>({ts.date})</small></span>
              <div className="timesheet-actions">
                <button className="view-button" onClick={() => viewReport(ts)}>View Report</button>
                <button className="pdf-button" onClick={() => generatePDF(ts.id)}>Generate PDF</button>
                <button className="delete-button" onClick={() => deleteTimesheet(ts.id)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ✅ Modal for viewing the timesheet report */}
      {selectedTimesheet && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Timesheet Report</h3>
            <p><strong>Project Name:</strong> {selectedTimesheet.project_name}</p>
            <p><strong>Project Cost Number:</strong> {selectedTimesheet.project_cost_number}</p>
            <p><strong>Worker Name:</strong> {selectedTimesheet.worker_name}</p>
            <p><strong>Date:</strong> {selectedTimesheet.date}</p>
            <p><strong>Job Description:</strong> {selectedTimesheet.job_description}</p>
            <button className="close-button" onClick={closeModal}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;