import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import axios from "axios";
import "./Dashboard.css"; // Import CSS for styling

const Dashboard = () => {
  const [timesheets, setTimesheets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate(); // Initialize navigation

  useEffect(() => {
    const fetchTimesheets = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          setError("User not authenticated. Please log in.");
          setLoading(false);
          return;
        }

        const response = await axios.get("http://127.0.0.1:5000/timesheets", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.length === 0) {
          setError("No timesheets found. Please create a new timesheet.");
        } else {
          setTimesheets(response.data);
        }
      } catch (err) {
        console.error("Error fetching timesheets:", err.response ? err.response.data : err.message);
        setError("Failed to load timesheets. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchTimesheets();
  }, []);

  return (
    <div className="dashboard-container">
      <h2>Dashboard</h2>

      <button className="create-button" onClick={() => navigate("/submit-timesheet")}>
        + Create New Timesheet
      </button> {/* Button to navigate to form */}

      {loading ? (
        <p>Loading timesheets...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : (
        timesheets.map((ts) => (
          <div key={ts.id} className="timesheet-card">
            <h4>{ts.project_name}</h4>
            <p>{ts.job_description}</p>
            <button onClick={() => window.open(`http://127.0.0.1:5000/generate_pdf/${ts.id}`)}>
              Generate PDF
            </button>
          </div>
        ))
      )}
    </div>
  );
};

export default Dashboard;
