import React from "react";
import { Routes, Route } from "react-router-dom";
import CustomAppBar from "./components/AppBar";
import Home from "./pages/Home";
import ContactLookup from "./pages/ContactLookup";
import BusinessLookup from "./pages/BusinessLookup";
import { RecentSearchesProvider } from "./context/RecentSearchesContext";


function App() {
  return (
    <>
    <RecentSearchesProvider>
      <CustomAppBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/contact-lookup" element={<ContactLookup />} />
        <Route path="/business-campaign-lookup" element={<BusinessLookup />} />
      </Routes>
    </RecentSearchesProvider>
    </>
  );
}

export default App;
