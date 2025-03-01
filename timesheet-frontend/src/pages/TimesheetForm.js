import React, { useState } from "react";
import axios from "axios";
import SignatureCanvas from "react-signature-canvas";
import { useNavigate } from "react-router-dom";

const TimesheetForm = () => {
  const [project_name, setProjectName] = useState("");
  const [project_cost_number, setCostNumber] = useState("");
  const [worker_name, setWorkerName] = useState("");
  const [date, setDate] = useState("");
  const [job_description, setJobDescription] = useState("");
  const [signature, setSignature] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("token");

    const formData = {
      project_name,
      project_cost_number,
      worker_name,
      date,
      job_description,
      signature_1: signature?.toDataURL(),
    };

    console.log("Submitting Data:", formData);

    try {
      await axios.post("http://127.0.0.1:5000/submit_timesheet", formData, {
        headers: { Authorization: `Bearer ${token}` },
      });

      alert("Timesheet submitted!");
      navigate("/dashboard");
    } catch (error) {
      console.error("Error submitting timesheet:", error.response ? error.response.data : error.message);
    }
  };

  return (
    <div>
      <h2>Submit Timesheet</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Project Name" onChange={(e) => setProjectName(e.target.value)} required />
        <input type="text" placeholder="Project Cost Number" onChange={(e) => setCostNumber(e.target.value)} required />
        <input type="text" placeholder="Worker Name" onChange={(e) => setWorkerName(e.target.value)} required />
        <input type="date" onChange={(e) => setDate(e.target.value)} required />
        <textarea placeholder="Job Description" onChange={(e) => setJobDescription(e.target.value)} required />
        <SignatureCanvas ref={(ref) => setSignature(ref)} penColor="black" canvasProps={{ width: 400, height: 150, className: "sigCanvas" }} />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default TimesheetForm;
