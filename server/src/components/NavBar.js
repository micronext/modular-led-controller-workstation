import React from 'react'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Typography from '@material-ui/core/Typography'
import './NavBar.css'
const NavBar = () => {
    return(
        <div id="navbar">
        <AppBar position="static">
            <Toolbar>
                <Typography variant="title" color="inherit">
                Audio Reactive LED Strip
                </Typography>
            </Toolbar>
        </AppBar>
        </div>
    )
}
export default NavBar;