import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';

const MetadataComparison = ({ data }) => {
  const formatMetadata = () => {
    if (!data) return [];

    const { main_app, competitors } = data;
    return [
      {
        appId: main_app.app_id,
        isMain: true,
        ...main_app.details,
      },
      ...competitors.map(comp => ({
        appId: comp.app_id,
        isMain: false,
        ...comp.details,
      })),
    ];
  };

  const renderMetadataTable = () => (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Metadata</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>
                {app.isMain ? (
                  <Chip label="Your App" color="primary" size="small" />
                ) : (
                  'Competitor'
                )}
                <Typography variant="caption" display="block">
                  {app.appId}
                </Typography>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell>Title</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>{app.title}</TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Title Length</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>{app.title?.length || 0}</TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Description Length</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>
                {app.description?.length || 0}
              </TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Category</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>{app.category}</TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Rating</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>{app.score?.toFixed(2)}</TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Reviews</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>
                {app.reviews?.toLocaleString()}
              </TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Installs</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>{app.installs}</TableCell>
            ))}
          </TableRow>
          <TableRow>
            <TableCell>Last Updated</TableCell>
            {formatMetadata().map(app => (
              <TableCell key={app.appId}>
                {new Date(app.updated * 1000).toLocaleDateString()}
              </TableCell>
            ))}
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box>
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Metadata Comparison
        </Typography>
        {renderMetadataTable()}
      </Paper>
    </Box>
  );
};

export default MetadataComparison;