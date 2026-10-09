import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Card,
  CardContent,
  IconButton,
  List,
  ListItemButton,
  CircularProgress,
  Divider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import EmailIcon from "@mui/icons-material/Email";
import XIcon from "@mui/icons-material/X";
import InstagramIcon from "@mui/icons-material/Instagram";
import LinkedInIcon from "@mui/icons-material/LinkedIn";
import FacebookIcon from "@mui/icons-material/Facebook";
import { useRecentSearches } from "../context/RecentSearchesContext"; // Import context



export default function ContactLookup() {
  const [searchQuery, setSearchQuery] = useState("");
  const [contact, setContact] = useState(null);
  const [employment, setEmployment] = useState([]);
  const [affiliations, setAffiliations] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [graphLoading, setGraphLoading] = useState(false);
  const [graphModalOpen, setGraphModalOpen] = useState(false);
  const [graphUrl, setGraphUrl] = useState(""); // Stores the graph URL
  const { addRecentSearch } = useRecentSearches(); // Get function from context

  useEffect(() => {
    const nameFromStorage = localStorage.getItem("recentSearch");
    if (nameFromStorage) {
      setSearchQuery(nameFromStorage);
      handleSuggestionClick(nameFromStorage); // Auto-trigger search
      localStorage.removeItem("recentSearch"); // Clear after use
    }
  }, []); // Run once when the component mounts


  // Handle typing in search box
  const handleSearchInput = async (event) => {
    const query = event.target.value;
    setSearchQuery(query);

    if (query.length > 1) {
      try {
        setLoading(true);
        const response = await axios.get(`http://127.0.0.1:5000/api/contacts/suggestions?query=${query}`);
        setLoading(false);
        
        if (response.data && response.data.suggestions.length > 0) {
          setSuggestions(response.data.suggestions);
        } else {
          setSuggestions([]);
        }
      } catch (err) {
        setLoading(false);
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
    }
  };

  // Handle selecting a name from dropdown
  const handleSuggestionClick = async (selectedName) => {
    setSearchQuery(selectedName);
    setSuggestions([]); // Hide dropdown after selection

    try {
      setLoading(true);
      const response = await axios.get(`http://127.0.0.1:5000/api/contacts/search`, {
        params: { name: selectedName }
      });
      setLoading(false);

      if (response.data.person) {
        setContact(response.data.person);
        setEmployment(response.data.employment || []);
        setAffiliations(response.data.affiliations || []);
        setError("");

        addRecentSearch(selectedName); // Now updates AppBar immediately

      } else {
        setError("No contact found.");
        setContact(null);
        setEmployment([]);
        setAffiliations([]);
      }
    } catch (err) {
      setLoading(false);
      setError("No contact found.");
      setContact(null);
      setEmployment([]);
      setAffiliations([]);
      console.error("API Error on Contact Fetch:", err.response ? err.response.data : err);
    }
  };

   // Handle Generate Contact Graph API Call
   const handleGenerateGraph = async () => {
    if (!contact) {
      setError("Please search for a contact first.");
      return;
    }

    setGraphLoading(true);

    try {
      const response = await axios.post(`http://127.0.0.1:5000/api/contacts/generate-graph`, {
        name: contact.name
      });

      setGraphLoading(false);

      if (response.data.success) {
        setGraphUrl(`http://127.0.0.1:5000/${response.data.graph_url}`);
        setGraphModalOpen(true); // Open the modal
      } else {
        setError("Failed to generate graph.");
      }
    } catch (err) {
      setGraphLoading(false);
      setError("Error generating graph.");
      console.error("Graph API Error:", err.response ? err.response.data : err);
    }
  };


  return (
    <Box sx={{ display: "flex", flexDirection: "column", padding: "30px", marginLeft: "300px" }}>
      
      {/* Search Bar with Dropdown */}
      <Box sx={{ position: "relative", width: "80%", alignSelf: "center" }}>
        <TextField
          variant="outlined"
          placeholder="Search for a contact..."
          fullWidth
          value={searchQuery}
          onChange={handleSearchInput}
          sx={{
            marginBottom: "5px",
            backgroundColor: "#f8f8f8",
            borderRadius: "8px",
          }}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: loading ? <CircularProgress size={20} /> : null,
            }
          }}
        />

        {/* Dropdown Suggestions */}
        {suggestions.length > 0 && (
          <List
            sx={{
              position: "absolute",
              width: "100%",
              backgroundColor: "white",
              boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)",
              borderRadius: "8px",
              zIndex: 10,
              maxHeight: "200px",
              overflowY: "auto",
            }}
          >
            {suggestions.map((suggestion, index) => (
              <ListItemButton
                key={index}
                onClick={() => handleSuggestionClick(suggestion.Label)}
                sx={{ "&:hover": { backgroundColor: "#f0f0f0" } }}
              >
                {suggestion.Label}
              </ListItemButton>
            ))}
          </List>
        )}
      </Box>

      {/* Error Message */}
      {error && <Typography color="error" sx={{ textAlign: "center", fontSize: "1.1rem" }}>{error}</Typography>}

      {/* Contact Information */}
      {contact && (
        <Box sx={{ display: "flex", gap: "40px" }}>
          {/* Left Side: Personal Details */}
          <Box sx={{ flex: 1 }}>
            <Card sx={{ padding: "20px", borderRadius: "12px", boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)" }}>
              <CardContent>
                <Typography variant="h5" fontWeight="bold">PERSONAL AND CONTACT INFORMATION</Typography>
                <Typography variant="h6" fontWeight="bold">{contact.name}</Typography>
                <Typography>Phone: {contact.phone || "N/A"}</Typography>
                <Typography>Email: {contact.email || "N/A"}</Typography>
                <Typography sx={{ marginTop: "10px" }}>
                  Home Address: <strong>{contact.address || "Unavailable"}</strong>
                </Typography>
                <Typography>
                  Work Address: {contact.workAddress || "N/A"}
                </Typography>

                {/* Social Media Icons BELOW Personal Info */}
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: "flex", justifyContent: "center", gap: "10px" }}>
                {contact.InstagramLink !== "N/A" && <IconButton component="a" href={contact.InstagramLink} target="_blank"><InstagramIcon /></IconButton>}
                {contact.xLink !== "N/A" && <IconButton component="a" href={contact.xLink} target="_blank"><XIcon /></IconButton>}
                {contact.LinkedInLink !== "N/A" && <IconButton component="a" href={contact.LinkedInLink} target="_blank"><LinkedInIcon /></IconButton>}
                {contact.FacebookLink !== "N/A" && <IconButton component="a" href={contact.FacebookLink} target="_blank"><FacebookIcon /></IconButton>}
              </Box>
              </CardContent>
            </Card>
          </Box>
          
          {/* Right Side: Professional History */}
          <Box sx={{ flex: 1 }}>
            <Card sx={{ padding: "20px", borderRadius: "12px", boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)" }}>
              <CardContent>
                <Typography variant="h5" fontWeight="bold">PROFESSIONAL HISTORY</Typography>
                <Typography>Job: <strong>{contact.job}</strong></Typography>
                <Typography>Company: <strong>{contact.company}</strong></Typography>

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" fontWeight="bold">Prior Employment</Typography>
                {employment.length > 0 ? employment.map((job, index) => (
                  <Typography key={index}>{job["Year Start"]} - {job["Year End"]}: {job.Role}, {job.Company}</Typography>
                )) : <Typography>No employment history available.</Typography>}

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" fontWeight="bold">Additional Organization Affiliations</Typography>
                {affiliations.length > 0 ? affiliations.map((aff, index) => (
                  <Typography key={index}>{aff["Year Start"]} - {aff["Year End"]}: {aff.Role}, {aff.Organization}</Typography>
                )) : <Typography>No affiliations available.</Typography>}
              </CardContent>
            </Card>
          </Box>
        </Box>
      )}

      {/* Generate Contact Graph Button */}
      {contact && (
        <Box sx={{ display: "flex", justifyContent: "flex-end", marginTop: "20px" }}>
          <Button
            variant="contained"
            sx={{ backgroundColor: "#2c3c64", color: "white", padding: "10px 20px" }}
            onClick={handleGenerateGraph}
            disabled={graphLoading}
          >
            {graphLoading ? <CircularProgress size={20} sx={{ color: "white" }} /> : "Generate Contact Graph"}
          </Button>
        </Box>
      )}

{/* Graph Modal */}
      <Dialog
        open={graphModalOpen}
        onClose={() => setGraphModalOpen(false)}
        fullWidth
        maxWidth="lg"
      >
        <DialogTitle>Contact Graph for {contact?.name}</DialogTitle>
        <DialogContent>
          {graphUrl && (
            <iframe
              src={graphUrl}
              width="100%"
              height="600px"
              style={{ border: "none" }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}
