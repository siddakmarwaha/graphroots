import React from "react";
import { Box, Typography } from "@mui/material";

export default function Home() {
  return (
    <Box sx={{ padding: "20px", marginLeft: "300px" }}>
      <Typography variant="h4">Welcome to Graphroots</Typography>
      <Typography variant="body1" sx={{ marginTop: "10px" }}>
        This is the homepage. Use the sidebar to navigate.
      </Typography>
    </Box>
  );
}
