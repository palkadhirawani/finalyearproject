import React from "react";
import { useTheme } from '@mui/material/styles';
import styled from "styled-components";
import { Box, Button, ButtonGroup, Divider, List, ListItem, ListItemText, ListSubheader } from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2";
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { ColorModeContext, tokens } from "../theme";
import { useState, useContext, useEffect } from "react";
import { ArcElement, Tooltip, Legend } from 'chart.js';
import {Chart as ChartJS} from 'chart.js/auto';
import { Chart } from "react-chartjs-2";
// import { Chart as ChartJS, registerables } from 'chart.js';
// import { Chart } from 'react-chartjs-2'
import { mockDataTeam } from "../data/mockData";
import { useParams } from "react-router-dom";
import ChartDisplay from "../components/ChartDisplay";
import ChangeTitle from "../components/CCTitleModal";
import ChangeColor from "../components/CCColorModal";
import ChangeXLabel from "../components/CCXLabelModal";
import ChangeYLabel from "../components/CCYLabelModal";



// ChartJS.register(...registerables);
ChartJS.register(ArcElement, Tooltip, Legend);

function containsUppercase(str) {
    return Boolean(str.match(/[A-Z]/));
}

function IndividualChart ({chart_id}) {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const colorMode = useContext(ColorModeContext);
    const {wid}  = useParams()
    //console.log(wid)
    const {text} = useParams();

    // const colourPalette = [
    //     {
    //         "Light": ["#B983FF", "#94B3FD", "#B9F3FC", "#A0FFE6", "#D0F58B"]
    //     },
    //     {
    //         "Dark": ["#37306B", "#66347F", "#9E4784", "#E36075", "#DE834D", "#E2AE29"]
    //     },
    //     {
    //         "Yellow": ["#C09C22", "#FFCA1A", "#FFD94D", "#FFE880", "#FFF099", "#FFFFCC"]
    //     },
    //     {
    //         "Blue": ["#1E3F66", "#2E5984", "#528AAE", "#73A5C6", "#AAD1EC", "#D2E9FF"]
    //     },
    //     { "BG" :  [
    //         "rgba(75,192,192,1)",
    //         "#ecf0f1",
    //         "#50AF95",
    //         "#f3ba2f",
    //         "#2a71d0",
    //         "#ecf0f1",
    //         "#50AF95",
    //         "#f3ba2f",
    //         "#2a71d0",
    //     ]}
    // ];

    const colourPalette = [
        {
            "name": "Light",
            "palette": ["#B983FF", "#94B3FD", "#B9F3FC", "#A0FFE6", "#D0F58B"],
        },
        {
            "name": "Dark",
            "palette": ["#37306B", "#66347F", "#9E4784", "#E36075", "#DE834D", "#E2AE29"],
        },
        {
            "name": "Yellow",
            "palette": ["#C09C22", "#FFCA1A", "#FFD94D", "#FFE880", "#FFF099", "#FFFFCC"],
        },
        {
            "name": "Blue",
            "palette": ["#1E3F66", "#2E5984", "#528AAE", "#73A5C6", "#AAD1EC", "#D2E9FF"],
        },
    ]

    console.log(colourPalette[0].name);


    const [chart, setChart] =  useState([])
    const [chartTitle, setChartTitle] = useState('something something title');
    const [chartType, setChartType] = useState('pie');
    const [xLabel, setXLabel] = useState('')
    const [yLabel, setYLabel] = useState('')
    const [summary, setSummary] = useState('')
    const [color,setColor] = useState('')
    const [data,setData] = useState({})
    const [chartData, setChartData] = useState({
        labels: mockDataTeam.map((data) => data.name), 
        datasets: [
            {
                label: "User Age",
                data: mockDataTeam.map((data) => data.age),
                backgroundColor: [
                    "#B983FF", "#94B3FD", "#B9F3FC", "#A0FFE6", "#D0F58B"
                ],
                // borderColor: "black",
                // borderWidth: 2
            },
        ]
    });

    const [titleModalOpen, setTitleModalOpen] = useState(false);
    const [xLabelModalOpen, setXLabelModalOpen] = useState(false);
    const [yLabelModalOpen, setYLabelModalOpen] = useState(false);
    const [colorModalOpen, setColorModalOpen] = useState(false);

    
    //console.log(chart_id)

    const fetchChart = async () => {
        const response = await fetch( 
           chart_id?`http://127.0.0.1:8000/chart/${chart_id}`:`http://127.0.0.1:8000/chart/${text}`
        );
        const data = await response.json();
        setChart(data.response[0]);
        //console.log(data)
        console.log(data.response[0])
        const type = data.response[0].chart_type.split(" ")[0]
        const x_label = data.response[0].x_axis
        const y_label = data.response[0].y_axis
        const summary_data =  data.response[0].summary ? data.response[0].summary : null
        setColor(data.response[0].options.split(",")[2])
        console.log(data.response[0].options.split(", ")[2])
        setSummary(summary_data)
        setXLabel(x_label)
        setYLabel(y_label)
        setChartType(type)
        console.log(x_label, y_label)
      };

      const fetchWorkspace= async () => {
        const response = await fetch( 
          `http://127.0.0.1:8000/workspace/${wid}`
        );
        const data = await response.json();
        //console.log(data.response)
        const database_id = data.response[0].database
        //setChartData(data)
        fetchData(database_id)
        return data
      };

      const fetchData = async (id) => {
        const response = await fetch( 
          `http://127.0.0.1:8000/view-file/${id}`
        );
        const data = await response.json();
        
        //console.log(xLabel,yLabel)
        const x =  xLabel ? xLabel : 'name'
        const y = yLabel ? yLabel : 'maths'


        setData({
            "x_values" : data.map((data) => data[x]),
            "y_values" : data.map((data) => data[y]),
            "x_label" : x,
            "y_label" : y
        })
        console.log(color)
        console.log(data)
        //console.log(data.map((data) => data[y]),data.map((data) => data[x]))
        //store x array and y array values in a seperate variable and write it in labels and data.
        setChartData(
            {
                labels: data.map((data) => data[x]), // x-axis
                datasets: [
                    {
                        label: y,
                        data: data.map((data) => data[y]), // y-axis
                        backgroundColor: color==='Dark' ?  colourPalette[1].palette : (color==='Yellow' ? colourPalette[2].palette : (color==='Blue' ? colourPalette[3].palette : colourPalette[0].palette)) ,
                        // borderColor: "black",
                        // borderWidth: 2
                    },
                ]
            }
        )
        //setChartData(data)
        return data
      };

    const generateSummary = async ()=>{
        console.log(data)
        const data_columns = {
            x_values: data.x_values,
            y_values : data.y_values,
            chart_id: chart_id ?  chart_id : text,
            x_label : data.x_label,
            y_label : data.y_label
          }
          //console.log(data_columns)
    
          const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data_columns),
        };
        fetch(`http://127.0.0.1:8000/chart-summary/${chart_id ? chart_id : text}/`, requestOptions)
            .then(function (response) {
              // ...
              console.log(response);
              return response.json();
            }).then(function (body) {
              // ...
              console.log(body);
              window.location.reload()
            }).catch(err => {
                console.log(err)
            })
    }

    useEffect(() => {
        fetchChart();
        //fetchWorkspace()
    }, [text]);

    useEffect(() => {
        fetchWorkspace();
        //fetchWorkspace()
        //console.log(xLabel,yLabel)
    }, [xLabel, yLabel]);
      
    return(
        <Box sx={{display: "flex", marginRight: "-30px"}}>
            <Grid container xs={10} sx={{display: "flex", flexDirection: "column", maxWidth: "calc(100% - 220px)", paddingRight: "30px", margin: "0 auto"}} >
                {/* <Chart
                    type={chartType}
                    data={chartData}
                    options={{
                        plugins: {
                            title: {
                                display: true,
                                text: chart?.title
                            },
                        },
                        maintainAspectRatio: false,
                    }}
                    // {...props}
                /> */}
                <Grid item sx={{backgroundColor: "white", margin: "20px 0 30px !important", borderRadius: "14px", padding: "16px"}}>
                    <Chart
                        type={chartType}
                        data={chartData}
                        height={400}
                        options={{
                            plugins: {
                                title: {
                                    display: true,
                                    text: chart?.title
                                },
                            },
                            maintainAspectRatio: false,
                        }}
                        // {...props}
                    />
                    {/* <ChartDisplay chart_id={1} /> */}
                </Grid>
                <Grid item sx={{backgroundColor: "transparent", padding: "0"}}>
                    <Accordion defaultExpanded={true} sx={{boxShadow: "none", borderRadius: "14px !important"}}>
                        <AccordionSummary
                        expandIcon={<ExpandMoreIcon />}
                        aria-controls="panel1a-content"
                        sx={{padding: "0px 20px"}}
                        >
                        <Typography sx={{fontSize: "16px", fontWeight: "600"}}>Summary for the chart</Typography>
                        </AccordionSummary>
                        <AccordionDetails sx={{padding: "20px", borderTop: "1px solid rgb(0,0,0,0.1)"}}>
                        <Typography sx={{fontSize: "16px"}}>
                            {summary}
                        </Typography>
                        </AccordionDetails>
                    </Accordion>
                </Grid>
            </Grid>
            <Divider orientation="vertical" flexItem sx={{height: "97vh", margin: "-94px 0"}}/> 
            <Grid xs={2} sx={{padding: "0 20px", width: "220px"}}>
                <Button onClick={generateSummary} sx={{backgroundColor: "#1C1C1C", borderRadius: "8px", textTransform: "capitalize", padding: "6px", width: "100%", boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.4)"}}>
                    + Generate Summary
                </Button>
                <Box backgroundColor="#FFFFFF" marginTop="40px" boxShadow="0px 4px 10px rgba(0, 0, 0, 0.2)" borderRadius="8px">
                    <Button disabled sx={{backgroundColor: "#1C1C1C", borderRadius: "8px", textTransform: "capitalize", padding: "6px", width: "100%", cursor: "initial", color: "#f9f9f9 !important"}} >Customize Chart</Button>
                    <ButtonGroup orientation="vertical" aria-label="vertical outlined button group" sx={{margin: "10px 0", width: "100%"}}>
                        <WhiteButtons onClick={() => {setTitleModalOpen(true)}}>Add/change title</WhiteButtons>
                        <WhiteButtons onClick={() => {setColorModalOpen(true)}}>Change color palette</WhiteButtons>
                        <WhiteButtons onClick={() => {setXLabelModalOpen(true)}}>Change x label</WhiteButtons>
                        <WhiteButtons onClick={() => {setYLabelModalOpen(true)}}>Change y label</WhiteButtons>
                        <WhiteButtons>Add legend</WhiteButtons>
                    </ButtonGroup>
                </Box>
            </Grid>
            <ChangeTitle titleModalOpen={titleModalOpen} setTitleModalOpen={setTitleModalOpen} chartDetails={chart}/>
            <ChangeColor colorModalOpen={colorModalOpen} setColorModalOpen={setColorModalOpen} chartDetails={chart}/>
            <ChangeXLabel xLabelModalOpen={xLabelModalOpen} setXLabelModalOpen={setXLabelModalOpen} chartDetails={chart}/>
            <ChangeYLabel yLabelModalOpen={yLabelModalOpen} setYLabelModalOpen={setYLabelModalOpen} chartDetails={chart}/>
        </Box>
    )
}

export default IndividualChart;

const WhiteButtons =  styled.button`
    background-color: white;
    color: #1c1c1c !important;
    text-transform: initial !important;
    border: none !important;
    font-size: 14px;
    text-align: left !important;
    padding: 9px 20px;
    cursor: pointer;
    &:hover {
        background-color: rgba(220, 226, 248, 0.6);
    }
`