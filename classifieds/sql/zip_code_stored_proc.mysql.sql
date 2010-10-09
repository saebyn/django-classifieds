DELIMITER $$  
 
DROP   FUNCTION  IF EXISTS `GetDistance`$$  
 
CREATE   FUNCTION  `GetDistance`(  
 lat1  double (9,6),  
 lon1  double (9,6),  
 lat2  double (9,6),  
 lon2  double (9,6)  
)  RETURNS   double (10,5)  DETERMINISTIC
BEGIN  
  DECLARE  x  double (21,20);  
  DECLARE  pi  double (21,20);  
  SET  pi = 3.14159265358979323846;  
  SET  x = sin( lat1 * pi/180 ) * sin( lat2 * pi/180  ) + cos(  
 lat1 *pi/180 ) * cos( lat2 * pi/180 ) * cos(  abs( (lon2 * pi/180) -  
 (lon1 *pi/180) ) );  
  SET  x = atan( ( sqrt( 1- power( x, 2 ) ) ) / x );  
  RETURN  ( 1.852 * 60.0 * ((x/pi)*180) ) / 1.609344;  
END $$

DROP   PROCEDURE  IF EXISTS `GetNearbyZipCodes`$$  
 
CREATE   PROCEDURE  `GetNearbyZipCodes`(  
    zipbase  varchar (6),  
    range  numeric (15)  
)  
BEGIN  
DECLARE  lat3  double (9,6);  
DECLARE  long3  double (9,6);  
DECLARE  rangeFactor  double (7,6);  
SET  rangeFactor = 0.014457;  
SELECT  latitude,longitude  into  lat3,long3  FROM  classifieds_zipcode  WHERE  zipcode = zipbase;  
SELECT  B.zipcode  
FROM  classifieds_zipcode  AS  B   
WHERE    
 B.latitude  BETWEEN  lat3-(range*rangeFactor)  AND  lat3+(range*rangeFactor)  
  AND  B.longitude  BETWEEN  long3-(range*rangeFactor)  AND  long3+(range*rangeFactor)  
  AND  GetDistance(lat3,long3,B.latitude,B.longitude)  <= range;  
END $$  
 
DELIMITER ;
