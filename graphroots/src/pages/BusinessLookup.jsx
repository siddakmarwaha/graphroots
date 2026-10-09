import React, { useState } from "react";
import axios from "axios";
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  Button,
  IconButton,
  ListItemButton,
  Dialog,
  DialogTitle,
  DialogContent,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import EmailIcon from "@mui/icons-material/Email";
import TwitterIcon from "@mui/icons-material/Twitter";
import InstagramIcon from "@mui/icons-material/Instagram";
import LinkedInIcon from "@mui/icons-material/LinkedIn";
import FacebookIcon from "@mui/icons-material/Facebook";

export default function BusinessLookup() {
  const [searchQuery, setSearchQuery] = useState("");
  const [business, setBusiness] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestions, setSuggestions] = useState([]);

  const [graphLoading, setGraphLoading] = useState(false);
  const [graphModalOpen, setGraphModalOpen] = useState(false);
  const [graphUrl, setGraphUrl] = useState("");  

  const handleGenerateBusinessGraph = async () => {
    if (!business) {
      setError("Please search for a business first.");
      return;
    }
  
    setGraphLoading(true);
  
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/business/generate-graph", {
        name: business.name
      });
  
      setGraphLoading(false);
  
      if (response.data.success) {
        setGraphUrl(`http://127.0.0.1:5000/${response.data.graph_url}`);
        setGraphModalOpen(true);
      } else {
        setError("Failed to generate business graph.");
      }
    } catch (err) {
      setGraphLoading(false);
      setError("Error generating graph.");
      console.error("Business Graph API Error:", err.response ? err.response.data : err);
    }
  };
  


  const handleSuggestionClick = async (selectedName) => {
    setSearchQuery(selectedName);
    setSuggestions([]);
    await handleSearch(selectedName);
  };

  const handleSearch = async (customQuery) => {
    const query = customQuery || searchQuery;
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/business/search`, {
        params: { name: query },
      });

      setLoading(false);
      if (response.data.business) {
        setBusiness(response.data.business);
        setEmployees(response.data.employees || []);
        setConnections(response.data.connections || []);
      } else {
        setError("No business found.");
        setBusiness(null);
        setEmployees([]);
        setConnections([]);
      }
    } catch (err) {
      setLoading(false);
      setError("Error fetching business data.");
      console.error("API Error:", err.response ? err.response.data : err);
    }
  };

  const handleSearchInput = async (e) => {
    const query = e.target.value;
    setSearchQuery(query);

    if (query.length > 1) {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/api/business/suggestions?query=${query}`);
        setSuggestions(response.data.suggestions || []);
      } catch {
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", padding: "30px", marginLeft: "300px" }}>
      {/* Search Bar with Suggestions */}
      <Box sx={{ position: "relative", width: "80%", alignSelf: "center" }}>
        <TextField
          variant="outlined"
          placeholder="Search for a business..."
          fullWidth
          value={searchQuery}
          onChange={handleSearchInput}
          sx={{ marginBottom: "5px", backgroundColor: "#f8f8f8", borderRadius: "8px" }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: loading ? <CircularProgress size={20} /> : null,
          }}
        />
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
            {suggestions.map((s, index) => (
              <ListItemButton
                key={index}
                onClick={() => handleSuggestionClick(s.Label)}
                sx={{ "&:hover": { backgroundColor: "#f0f0f0" } }}
              >
                {s.Label}
              </ListItemButton>
            ))}
          </List>
        )}
        <Button variant="contained" onClick={() => handleSearch()} sx={{ marginTop: "10px" }}>
          Search
        </Button>
      </Box>

      {/* Error Message */}
      {error && <Typography color="error" sx={{ textAlign: "center", fontSize: "1.1rem" }}>{error}</Typography>}

      {/* Business Details */}
      {business && (
        <Box sx={{ display: "flex", gap: "40px", marginTop: "20px" }}>
          <Box sx={{ flex: 1 }}>
            <Card sx={{ padding: "20px", borderRadius: "12px", boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)" }}>
              <CardContent>
                <Typography variant="h5" fontWeight="bold">BUSINESS CONTACT INFORMATION</Typography>
                <Typography variant="h6" fontWeight="bold">{business.name}</Typography>
                <Typography>Phone: {business.phone || "N/A"}</Typography>
                <Typography>Email: {business.email || "N/A"}</Typography>
                <Typography>Work Address: {business.address || "Unavailable"}</Typography>
                <Typography>Financial Information: {business.financial || "Unavailable"}</Typography>
                <Typography>Business Sector: {business.sector || "N/A"}</Typography>

                <Divider sx={{ my: 2 }} />
                <Box sx={{ display: "flex", justifyContent: "center", gap: "10px" }}>
                  {business.email && <IconButton><EmailIcon /></IconButton>}
                  {business.twitter && <IconButton component="a" href={business.twitter} target="_blank"><TwitterIcon /></IconButton>}
                  {business.instagram && <IconButton component="a" href={business.instagram} target="_blank"><InstagramIcon /></IconButton>}
                  {business.linkedin && <IconButton component="a" href={business.linkedin} target="_blank"><LinkedInIcon /></IconButton>}
                  {business.facebook && <IconButton component="a" href={business.facebook} target="_blank"><FacebookIcon /></IconButton>}
                </Box>
              </CardContent>
            </Card>
          </Box>

          {/* Employees & Connections */}
          <Box sx={{ flex: 1 }}>
            <Card sx={{ padding: "20px", borderRadius: "12px", boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)" }}>
              <CardContent>
                <Typography variant="h6" fontWeight="bold">Relevant Employees</Typography>
                {employees.length > 0 ? (
                  <List>
                    {employees.map((emp, index) => (
                      <ListItem key={index}>
                        <ListItemText 
                          primary={emp.Label} 
                          secondary={`${emp.Job} | Email: ${emp.Email} | Phone: ${emp.PhoneNumber} | ${emp.Status}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography>No employees found.</Typography>
                )}

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" fontWeight="bold">Additional Connections</Typography>
                {connections.length > 0 ? (
                  <List>
                    {connections.map((conn, index) => (
                      <ListItem key={index}>
                        <ListItemText 
                          primary={`${conn["Year Start"]}-${conn["Year End"]}`} 
                          secondary={`${conn["Role"]}, ${conn["Organization"]}`} 
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography>No connections available.</Typography>
                )}
              </CardContent>
            </Card>
          </Box>
        </Box>
      )}
      {business && (
        <Box sx={{ display: "flex", justifyContent: "flex-end", marginTop: "20px" }}>
          <Button
            variant="contained"
            sx={{ backgroundColor: "#2c3c64", color: "white", padding: "10px 20px" }}
            onClick={handleGenerateBusinessGraph}
            disabled={graphLoading}
          >
            {graphLoading ? <CircularProgress size={20} sx={{ color: "white" }} /> : "Generate Business Graph"}
          </Button>
        </Box>
      )}


      <Dialog
        open={graphModalOpen}
        onClose={() => setGraphModalOpen(false)}
        fullWidth
        maxWidth="lg"
      >
        <DialogTitle>Business Graph for {business?.name}</DialogTitle>
        <DialogContent>
          {graphUrl && (
            <iframe
              src={graphUrl}
              width="100%"
              height="600px"
              style={{ border: "none" }}
              title="Business Graph"
            />
          )}
        </DialogContent>
      </Dialog>

    </Box>
    
  );
}
