-- =====================================================
-- NAVDRISHTI: Construction Projects Table
-- Purpose: Store construction zones with spatial geometry
-- Author: NavDrishti Team
-- Date: December 16, 2025
-- =====================================================

-- Drop table if exists (for clean migration)
DROP TABLE IF EXISTS `construction_projects`;

-- Create construction_projects table
CREATE TABLE `construction_projects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique identifier for construction project',
    `project_name` VARCHAR(255) NOT NULL COMMENT 'Name of the construction project',
    `description` TEXT DEFAULT NULL COMMENT 'Detailed description of the work',
    `start_date` DATE NOT NULL COMMENT 'Planned start date of construction',
    `end_date` DATE NOT NULL COMMENT 'Expected completion date',
    `status` ENUM('planned', 'active', 'completed', 'cancelled') NOT NULL DEFAULT 'planned' 
        COMMENT 'Current status of the project',
    
    -- Spatial columns for geospatial analysis
    `zone_geometry` GEOMETRY NOT NULL COMMENT 'Polygon representing the construction zone (GeoJSON format)',
    `impact_radius_geometry` GEOMETRY DEFAULT NULL COMMENT 'Calculated isochrone/buffer zone showing impact area',
    
    -- Metadata
    `created_by` VARCHAR(100) DEFAULT NULL COMMENT 'User ID of project creator',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    -- Constraints
    CONSTRAINT `chk_dates` CHECK (`end_date` >= `start_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores construction projects with spatial geometry for traffic impact analysis';

-- Create spatial indexes for fast geospatial queries
-- SPATIAL indexes are critical for MySQL spatial operations (ST_Contains, ST_Intersects, etc.)
CREATE SPATIAL INDEX `idx_zone_geometry` ON `construction_projects` (`zone_geometry`);
CREATE SPATIAL INDEX `idx_impact_radius` ON `construction_projects` (`impact_radius_geometry`);

-- Create regular indexes for common queries
CREATE INDEX `idx_status` ON `construction_projects` (`status`);
CREATE INDEX `idx_date_range` ON `construction_projects` (`start_date`, `end_date`);
CREATE INDEX `idx_created_at` ON `construction_projects` (`created_at`);

-- =====================================================
-- SAMPLE QUERY PATTERNS (for government auditors)
-- =====================================================

-- Query 1: Find all active construction zones
-- SELECT id, project_name, start_date, end_date 
-- FROM construction_projects 
-- WHERE status = 'active' 
-- AND CURDATE() BETWEEN start_date AND end_date;

-- Query 2: Find construction zones intersecting a specific point (e.g., accident location)
-- SELECT id, project_name 
-- FROM construction_projects 
-- WHERE ST_Contains(zone_geometry, ST_GeomFromText('POINT(72.5714 23.0225)', 4326));

-- Query 3: Find construction zones within 5km of a coordinate
-- SELECT id, project_name, ST_Distance_Sphere(zone_geometry, ST_GeomFromText('POINT(72.5714 23.0225)', 4326)) AS distance_m
-- FROM construction_projects 
-- WHERE ST_Distance_Sphere(zone_geometry, ST_GeomFromText('POINT(72.5714 23.0225)', 4326)) <= 5000;

-- Query 4: Calculate total impact area (square kilometers)
-- SELECT SUM(ST_Area(impact_radius_geometry)) / 1000000 AS total_impact_km2 
-- FROM construction_projects 
-- WHERE status = 'active';

-- =====================================================
-- NOTES FOR MAINTENANCE
-- =====================================================
-- 1. Always use ST_GeomFromGeoJSON() when inserting GeoJSON from frontend
-- 2. Always use ST_AsGeoJSON() when retrieving geometries for frontend
-- 3. Coordinate system: WGS84 (SRID 4326) - standard for web maps
-- 4. Backup this table before major migrations due to large GEOMETRY columns
