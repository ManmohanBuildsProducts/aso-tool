import React from 'react';
import { AppBar, Toolbar, Box } from '@mui/material';

const Header = () => {
  return (
    <AppBar position="static" color="transparent" elevation={0}>
      <Toolbar>
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', py: 2 }}>
          <img 
            src="https://badho.in/wp-content/uploads/2023/12/Badho-Logo-1.png" 
            alt="Badho Logo" 
            style={{ 
              height: '40px',
              marginRight: '20px'
            }}
          />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;