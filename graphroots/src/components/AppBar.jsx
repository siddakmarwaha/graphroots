import React from "react";
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  Toolbar,
  List,
  Typography,
  Divider,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";
import ContactsIcon from "@mui/icons-material/Contacts";
import BusinessIcon from "@mui/icons-material/Business";
import HistoryIcon from "@mui/icons-material/History";
import LogoutIcon from "@mui/icons-material/Logout";
import grassrootsLogo from "../assets/Grassrootshome.png"; // Ensure correct path
import { Link } from "react-router-dom";
import { useRecentSearches } from "../context/RecentSearchesContext";
import { useNavigate } from "react-router-dom";



const drawerWidth = 280;

export default function CustomAppBar() {
  // Top Navigation Items
  const navItems = [
    { text: "Home", icon: <HomeIcon />, link: "/" },
    { text: "Contact Lookup", icon: <ContactsIcon />, link: "/contact-lookup" },
    { text: "Business/Campaign Lookup", icon: <BusinessIcon />, link: "/business-campaign-lookup" },
  ];

  const { recentSearches } = useRecentSearches(); // Get recent searches from context
  const navigate = useNavigate(); // Hook for navigation

  const handleRecentSearchClick = (name) => {
    localStorage.setItem("recentSearch", name); // Store name in local storage
    navigate("/contact-lookup"); // Navigate to Contact Lookup
  };


  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />

      {/* Top AppBar - Overlapping the Drawer */}
      <AppBar
        position="absolute"
        sx={{
          backgroundColor: "#2E8B57",
          zIndex: (theme) => theme.zIndex.drawer + 1, // Ensures it stays above the drawer
          width: "100%",
          left: 0,
        }}
      >
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
          {/* Center: Title (No menu icon on the left) */}
          <Typography variant="h6">Graphroots</Typography>

          {/* Right Side: Grassroots Logo with Hyperlink */}
          <Box>
            <a href="https://www.grassrootsmidwest.com/" target="_blank" rel="noopener noreferrer">
              <img
                src={grassrootsLogo}
                alt="Grassroots Logo"
                style={{ height: "40px", width: "auto" }}
              />
            </a>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Left Drawer (Always Permanent) */}
      <Drawer
        variant="permanent"
        sx={{
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            position: "absolute", // Ensures AppBar overlaps
            top: 0,
          },
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            height: "100%",
            backgroundColor: "#2c3c64",
            color: "#ffffff",
            paddingTop: "64px", // Prevents overlap with AppBar
          }}
        >
          <Divider sx={{ borderColor: "#444" }} />

          {/* Top Navigation */}
          
          <List>
            {navItems.map((item, index) => (
              <ListItem key={index} disablePadding>
                <ListItemButton component={Link} to={item.link}>  {/* Correct way to use Link */}
                  <ListItemIcon sx={{ color: "#ffffff" }}>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          <Divider sx={{ borderColor: "#444", marginTop: "auto" }} />

          <Typography sx={{ padding: "16px", color: "#bbb" }}>Recently Accessed</Typography>
          <List>
            {recentSearches.length > 0 ? (
              recentSearches.map((search, index) => (
                <ListItem key={index} disablePadding>
                  <ListItemButton onClick={() => handleRecentSearchClick(search)}>
                    <ListItemIcon sx={{ color: "#ffffff" }}>
                      <HistoryIcon />
                    </ListItemIcon>
                    <ListItemText primary={search} />
                  </ListItemButton>
                </ListItem>
              ))
            ) : (
              <Typography sx={{ paddingLeft: "16px", color: "#bbb" }}>No recent searches</Typography>
            )}
          </List>

          {/* Logout Button */}
          <Divider sx={{ borderColor: "#444" }} />
          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon sx={{ color: "#ffffff" }}>
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </ListItemButton>
          </ListItem>
        </Box>
      </Drawer>
    </Box>
  );
}
