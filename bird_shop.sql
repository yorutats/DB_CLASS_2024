SET search_path TO birdshop;
CREATE TABLE Customer (
   cId SERIAL PRIMARY KEY,
   cName VARCHAR(100) NOT NULL,
   phone VARCHAR(20) NOT NULL
);
CREATE TABLE Supplier (
   sId SERIAL PRIMARY KEY,
   sName VARCHAR(100) NOT NULL,
   phone VARCHAR(20) NOT NULL,
   rating DECIMAL(2, 1) NOT NULL
);
CREATE TABLE BirdCareGuide (
   gId SERIAL PRIMARY KEY,
   gDesc TEXT NOT NULL,
   videoLink VARCHAR(255)
);
CREATE TABLE Bird (
   bId SERIAL PRIMARY KEY,
   sId INT REFERENCES Supplier(sId),
   gId INT REFERENCES BirdCareGuide(gId),
   bDesc TEXT NOT NULL,
   species VARCHAR(100) NOT NULL,
   price DECIMAL(10, 2) NOT NULL,
   stock INT NOT NULL
);
CREATE TABLE "order" (
   cId INT REFERENCES Customer(cId),
   orderTime TIMESTAMP NOT NULL,
   totalAmount DECIMAL(10, 2) NOT NULL,
   PRIMARY KEY (cId, orderTime)
);
CREATE TABLE record (
   bId INT NOT NULL,
   cId INT NOT NULL,
   orderTime TIMESTAMP NOT NULL,
   subAmount DECIMAL(10, 2) NOT NULL,
   rNum INT NOT NULL,
   PRIMARY KEY (bId, cId, orderTime, rNum),
   FOREIGN KEY (bId) REFERENCES Bird(bId),
   FOREIGN KEY (cId, orderTime) REFERENCES "order"(cId, orderTime)
);