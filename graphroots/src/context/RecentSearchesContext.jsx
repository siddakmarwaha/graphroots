import React, { createContext, useContext, useState, useEffect } from "react";

// Create Context
const RecentSearchesContext = createContext();

export const RecentSearchesProvider = ({ children }) => {
  const [recentSearches, setRecentSearches] = useState([]);

  // Load recent searches from localStorage on first render
  useEffect(() => {
    const storedSearches = JSON.parse(localStorage.getItem("recentSearches")) || [];
    setRecentSearches(storedSearches);
  }, []);

  // Function to update recent searches
  const addRecentSearch = (name) => {
    setRecentSearches((prevSearches) => {
      const updatedSearches = [name, ...prevSearches.filter(n => n !== name)].slice(0, 3);
      localStorage.setItem("recentSearches", JSON.stringify(updatedSearches));
      return updatedSearches;
    });
  };

  return (
    <RecentSearchesContext.Provider value={{ recentSearches, addRecentSearch }}>
      {children}
    </RecentSearchesContext.Provider>
  );
};

// Custom hook to use the context
export const useRecentSearches = () => useContext(RecentSearchesContext);
