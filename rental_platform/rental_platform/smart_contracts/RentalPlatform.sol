// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RentalPlatform {
    // 结构体定义
    struct User {
        string name;
        string email;
        bool isVerified;
        uint256 reputation;
        uint256 joinDate;
    }

    struct Property {
        address owner;
        string title;
        string description;
        uint256 price;
        bool isAvailable;
        uint256[] bookingIds;
        uint256 reputation;
    }

    struct Booking {
        address tenant;
        uint256 propertyId;
        uint256 startDate;
        uint256 endDate;
        uint256 totalPrice;
        bool isConfirmed;
        bool isCompleted;
    }

    struct Review {
        address reviewer;
        uint256 propertyId;
        uint256 rating;
        string comment;
        uint256 timestamp;
    }

    // 状态变量
    mapping(address => User) public users;
    mapping(uint256 => Property) public properties;
    mapping(uint256 => Booking) public bookings;
    mapping(uint256 => Review[]) public propertyReviews;
    
    uint256 public propertyCount;
    uint256 public bookingCount;

    // 事件定义
    event UserRegistered(address indexed user, string name, uint256 timestamp);
    event PropertyRegistered(uint256 indexed propertyId, address indexed owner, string title);
    event BookingCreated(uint256 indexed bookingId, uint256 indexed propertyId, address indexed tenant);
    event BookingConfirmed(uint256 indexed bookingId);
    event BookingCompleted(uint256 indexed bookingId);
    event ReviewSubmitted(uint256 indexed propertyId, address indexed reviewer, uint256 rating);

    // 修饰器
    modifier onlyRegisteredUser() {
        require(users[msg.sender].joinDate > 0, "User not registered");
        _;
    }

    modifier onlyPropertyOwner(uint256 _propertyId) {
        require(properties[_propertyId].owner == msg.sender, "Not property owner");
        _;
    }

    // 用户注册
    function registerUser(string memory _name, string memory _email) public {
        require(users[msg.sender].joinDate == 0, "User already registered");
        
        users[msg.sender] = User({
            name: _name,
            email: _email,
            isVerified: false,
            reputation: 0,
            joinDate: block.timestamp
        });

        emit UserRegistered(msg.sender, _name, block.timestamp);
    }

    // 注册房源
    function registerProperty(
        string memory _title,
        string memory _description,
        uint256 _price
    ) public onlyRegisteredUser {
        propertyCount++;
        
        properties[propertyCount] = Property({
            owner: msg.sender,
            title: _title,
            description: _description,
            price: _price,
            isAvailable: true,
            bookingIds: new uint256[](0),
            reputation: 0
        });

        emit PropertyRegistered(propertyCount, msg.sender, _title);
    }

    // 创建预订
    function createBooking(
        uint256 _propertyId,
        uint256 _startDate,
        uint256 _endDate
    ) public onlyRegisteredUser {
        require(_propertyId > 0 && _propertyId <= propertyCount, "Invalid property ID");
        require(properties[_propertyId].isAvailable, "Property not available");
        require(_startDate < _endDate, "Invalid dates");
        require(_startDate > block.timestamp, "Start date must be in the future");

        uint256 duration = _endDate - _startDate;
        uint256 totalPrice = properties[_propertyId].price * duration;

        bookingCount++;
        bookings[bookingCount] = Booking({
            tenant: msg.sender,
            propertyId: _propertyId,
            startDate: _startDate,
            endDate: _endDate,
            totalPrice: totalPrice,
            isConfirmed: false,
            isCompleted: false
        });

        properties[_propertyId].bookingIds.push(bookingCount);

        emit BookingCreated(bookingCount, _propertyId, msg.sender);
    }

    // 确认预订
    function confirmBooking(uint256 _bookingId) public {
        require(_bookingId > 0 && _bookingId <= bookingCount, "Invalid booking ID");
        Booking storage booking = bookings[_bookingId];
        require(properties[booking.propertyId].owner == msg.sender, "Not property owner");
        require(!booking.isConfirmed, "Booking already confirmed");

        booking.isConfirmed = true;
        properties[booking.propertyId].isAvailable = false;

        emit BookingConfirmed(_bookingId);
    }

    // 完成预订
    function completeBooking(uint256 _bookingId) public {
        require(_bookingId > 0 && _bookingId <= bookingCount, "Invalid booking ID");
        Booking storage booking = bookings[_bookingId];
        require(booking.isConfirmed, "Booking not confirmed");
        require(!booking.isCompleted, "Booking already completed");
        require(block.timestamp >= booking.endDate, "Booking period not ended");

        booking.isCompleted = true;
        properties[booking.propertyId].isAvailable = true;

        emit BookingCompleted(_bookingId);
    }

    // 提交评价
    function submitReview(
        uint256 _propertyId,
        uint256 _rating,
        string memory _comment
    ) public onlyRegisteredUser {
        require(_propertyId > 0 && _propertyId <= propertyCount, "Invalid property ID");
        require(_rating > 0 && _rating <= 5, "Rating must be between 1 and 5");

        // 检查用户是否租用过该房源
        bool hasBooked = false;
        for (uint256 i = 0; i < properties[_propertyId].bookingIds.length; i++) {
            uint256 bookingId = properties[_propertyId].bookingIds[i];
            if (bookings[bookingId].tenant == msg.sender && bookings[bookingId].isCompleted) {
                hasBooked = true;
                break;
            }
        }
        require(hasBooked, "Must have completed a booking to review");

        Review memory newReview = Review({
            reviewer: msg.sender,
            propertyId: _propertyId,
            rating: _rating,
            comment: _comment,
            timestamp: block.timestamp
        });

        propertyReviews[_propertyId].push(newReview);

        // 更新房源声誉
        uint256 totalRating = 0;
        for (uint256 i = 0; i < propertyReviews[_propertyId].length; i++) {
            totalRating += propertyReviews[_propertyId][i].rating;
        }
        properties[_propertyId].reputation = totalRating / propertyReviews[_propertyId].length;

        emit ReviewSubmitted(_propertyId, msg.sender, _rating);
    }

    // 获取房源评价
    function getPropertyReviews(uint256 _propertyId) public view returns (Review[] memory) {
        return propertyReviews[_propertyId];
    }

    // 获取用户信息
    function getUserInfo(address _user) public view returns (User memory) {
        return users[_user];
    }

    // 获取房源信息
    function getPropertyInfo(uint256 _propertyId) public view returns (Property memory) {
        return properties[_propertyId];
    }

    // 获取预订信息
    function getBookingInfo(uint256 _bookingId) public view returns (Booking memory) {
        return bookings[_bookingId];
    }
} 