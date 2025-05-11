// 区块链浏览器页面脚本

// 合约信息 - 从Django模板获取
const CONTRACT_ADDRESS = document.querySelector('a[href*="sepolia.etherscan.io/address/"]').textContent;
const SEPOLIA_RPC_URL = 'https://eth-sepolia.g.alchemy.com/v2/9LXOdanO569UkCCU0ZvCh-4aQsdibYpE'; // 通常你会想要通过Django传入这个值

// 合约 ABI - 包含与事件和函数相关的部分
const CONTRACT_ABI = [
    // 事件定义
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "bookingId",
          "type": "uint256"
        }
      ],
      "name": "BookingCompleted",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "bookingId",
          "type": "uint256"
        }
      ],
      "name": "BookingConfirmed",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "bookingId",
          "type": "uint256"
        },
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "propertyId",
          "type": "uint256"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "tenant",
          "type": "address"
        }
      ],
      "name": "BookingCreated",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "propertyId",
          "type": "uint256"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "string",
          "name": "title",
          "type": "string"
        }
      ],
      "name": "PropertyRegistered",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "propertyId",
          "type": "uint256"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "reviewer",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "rating",
          "type": "uint256"
        }
      ],
      "name": "ReviewSubmitted",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "UserRegistered",
      "type": "event"
    },
    // 查询函数
    {
      "inputs": [],
      "name": "bookingCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "propertyCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
];

// ethers.js 和 Web3 相关实例
let provider;
let contract;

// 页面 DOM 元素
const propertyCountEl = document.getElementById('property-count');
const bookingCountEl = document.getElementById('booking-count');
const allEventsEl = document.getElementById('all-events');
const userEventsEl = document.getElementById('user-events');
const propertyEventsEl = document.getElementById('property-events');
const bookingEventsEl = document.getElementById('booking-events');
const reviewEventsEl = document.getElementById('review-events');

// 辅助函数
function formatAddress(address) {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

function formatTimestamp(timestamp) {
    return new Date(timestamp * 1000).toLocaleString('zh-CN');
}

function formatTxHash(hash) {
    return `<a href="https://sepolia.etherscan.io/tx/${hash}" target="_blank" class="tx-hash">${hash.slice(0, 10)}...</a>`;
}

function formatAddressWithLink(address) {
    return `<a href="https://sepolia.etherscan.io/address/${address}" target="_blank" class="address-link">${formatAddress(address)}</a>`;
}

// 初始化区块链连接
async function initBlockchain() {
    try {
        // 连接到区块链网络
        provider = new ethers.providers.JsonRpcProvider(SEPOLIA_RPC_URL);
        
        // 创建合约实例
        contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
        
        // 加载基本信息
        await loadContractInfo();
        
        // 加载事件数据
        await loadEvents();
        
        // 设置实时监听
        setupEventListeners();
        
        console.log('区块链浏览器初始化成功');
    } catch (error) {
        console.error('初始化区块链连接失败:', error);
        showError('连接区块链网络失败，请检查网络连接后刷新页面。');
    }
}

// 加载合约基本信息
async function loadContractInfo() {
    try {
        // 获取房源数量
        const propertyCount = await contract.propertyCount();
        propertyCountEl.textContent = propertyCount.toString();
        
        // 获取预订数量
        const bookingCount = await contract.bookingCount();
        bookingCountEl.textContent = bookingCount.toString();
    } catch (error) {
        console.error('加载合约信息失败:', error);
        propertyCountEl.textContent = '获取失败';
        bookingCountEl.textContent = '获取失败';
    }
}

// 加载所有事件
async function loadEvents() {
    try {
        // 设置各表格为加载状态
        setLoading(allEventsEl);
        setLoading(userEventsEl);
        setLoading(propertyEventsEl);
        setLoading(bookingEventsEl);
        setLoading(reviewEventsEl);
        
        // 获取当前区块号
        const currentBlock = await provider.getBlockNumber();
        // 查询从 0 到当前区块的所有事件（或限制查询范围以提高性能）
        const startBlock = Math.max(0, currentBlock - 10000); // 限制为最近10000个区块
        
        // 定义要查询的事件类型
        const eventTypes = [
            'UserRegistered',
            'PropertyRegistered',
            'BookingCreated',
            'BookingConfirmed',
            'BookingCompleted',
            'ReviewSubmitted'
        ];
        
        // 收集所有事件
        let allEvents = [];
        let userEvents = [];
        let propertyEvents = [];
        let bookingEvents = [];
        let reviewEvents = [];
        
        // 逐个查询事件类型
        for (const eventType of eventTypes) {
            console.log(`查询事件: ${eventType}`);
            
            // 获取事件过滤器
            const filter = contract.filters[eventType]();
            
            // 查询事件历史
            const events = await contract.queryFilter(filter, startBlock, currentBlock);
            console.log(`找到 ${events.length} 个 ${eventType} 事件`);
            
            // 获取事件详情
            for (const event of events) {
                // 获取包含事件的交易细节
                const tx = await event.getTransaction();
                // 获取包含事件的区块细节
                const block = await event.getBlock();
                
                // 创建事件对象
                const eventObj = {
                    type: eventType,
                    data: event.args,
                    timestamp: block.timestamp,
                    txHash: tx.hash,
                    blockNumber: event.blockNumber
                };
                
                // 添加到所有事件列表
                allEvents.push(eventObj);
                
                // 根据事件类型添加到相应列表
                switch (eventType) {
                    case 'UserRegistered':
                        userEvents.push(eventObj);
                        break;
                    case 'PropertyRegistered':
                        propertyEvents.push(eventObj);
                        break;
                    case 'BookingCreated':
                    case 'BookingConfirmed':
                    case 'BookingCompleted':
                        bookingEvents.push(eventObj);
                        break;
                    case 'ReviewSubmitted':
                        reviewEvents.push(eventObj);
                        break;
                }
            }
        }
        
        // 按时间戳排序（最近的在前）
        allEvents.sort((a, b) => b.timestamp - a.timestamp);
        userEvents.sort((a, b) => b.timestamp - a.timestamp);
        propertyEvents.sort((a, b) => b.timestamp - a.timestamp);
        bookingEvents.sort((a, b) => b.timestamp - a.timestamp);
        reviewEvents.sort((a, b) => b.timestamp - a.timestamp);
        
        // 清空各表格
        allEventsEl.innerHTML = '';
        userEventsEl.innerHTML = '';
        propertyEventsEl.innerHTML = '';
        bookingEventsEl.innerHTML = '';
        reviewEventsEl.innerHTML = '';
        
        // 如果没有事件，显示无数据信息
        if (allEvents.length === 0) {
            allEventsEl.innerHTML = '<tr><td colspan="5" class="text-center py-3">暂无数据</td></tr>';
        } else {
            // 渲染所有事件
            allEvents.forEach(event => {
                const row = createEventRow(event);
                allEventsEl.appendChild(row);
            });
        }
        
        // 渲染用户注册事件
        if (userEvents.length === 0) {
            userEventsEl.innerHTML = '<tr><td colspan="4" class="text-center py-3">暂无用户注册数据</td></tr>';
        } else {
            userEvents.forEach(event => {
                const row = createUserEventRow(event);
                userEventsEl.appendChild(row);
            });
        }
        
        // 渲染房源注册事件
        if (propertyEvents.length === 0) {
            propertyEventsEl.innerHTML = '<tr><td colspan="5" class="text-center py-3">暂无房源注册数据</td></tr>';
        } else {
            propertyEvents.forEach(event => {
                const row = createPropertyEventRow(event);
                propertyEventsEl.appendChild(row);
            });
        }
        
        // 渲染预订事件
        if (bookingEvents.length === 0) {
            bookingEventsEl.innerHTML = '<tr><td colspan="6" class="text-center py-3">暂无预订数据</td></tr>';
        } else {
            bookingEvents.forEach(event => {
                const row = createBookingEventRow(event);
                bookingEventsEl.appendChild(row);
            });
        }
        
        // 渲染评价事件
        if (reviewEvents.length === 0) {
            reviewEventsEl.innerHTML = '<tr><td colspan="5" class="text-center py-3">暂无评价数据</td></tr>';
        } else {
            reviewEvents.forEach(event => {
                const row = createReviewEventRow(event);
                reviewEventsEl.appendChild(row);
            });
        }
        
    } catch (error) {
        console.error('加载事件数据失败:', error);
        showError('加载区块链事件数据失败，请稍后再试。');
    }
}

// 设置事件监听器，实时监听新事件
function setupEventListeners() {
    // 监听用户注册事件
    contract.on('UserRegistered', (user, name, timestamp, event) => {
        console.log('新用户注册事件:', user, name, timestamp);
        handleNewEvent('UserRegistered', {user, name, timestamp}, event);
    });
    
    // 监听房源注册事件
    contract.on('PropertyRegistered', (propertyId, owner, title, event) => {
        console.log('新房源注册事件:', propertyId, owner, title);
        handleNewEvent('PropertyRegistered', {propertyId, owner, title}, event);
    });
    
    // 监听预订创建事件
    contract.on('BookingCreated', (bookingId, propertyId, tenant, event) => {
        console.log('新预订创建事件:', bookingId, propertyId, tenant);
        handleNewEvent('BookingCreated', {bookingId, propertyId, tenant}, event);
    });
    
    // 监听预订确认事件
    contract.on('BookingConfirmed', (bookingId, event) => {
        console.log('预订确认事件:', bookingId);
        handleNewEvent('BookingConfirmed', {bookingId}, event);
    });
    
    // 监听预订完成事件
    contract.on('BookingCompleted', (bookingId, event) => {
        console.log('预订完成事件:', bookingId);
        handleNewEvent('BookingCompleted', {bookingId}, event);
    });
    
    // 监听评价提交事件
    contract.on('ReviewSubmitted', (propertyId, reviewer, rating, event) => {
        console.log('新评价提交事件:', propertyId, reviewer, rating);
        handleNewEvent('ReviewSubmitted', {propertyId, reviewer, rating}, event);
    });
}

// 处理新事件
async function handleNewEvent(eventType, eventArgs, eventObj) {
    try {
        // 获取包含事件的交易细节
        const tx = await eventObj.getTransaction();
        // 获取包含事件的区块细节
        const block = await eventObj.getBlock();
        
        // 创建事件对象
        const event = {
            type: eventType,
            data: eventArgs,
            timestamp: block.timestamp,
            txHash: tx.hash,
            blockNumber: eventObj.blockNumber
        };
        
        // 创建事件行
        let row;
        
        // 根据事件类型处理
        switch (eventType) {
            case 'UserRegistered':
                row = createUserEventRow(event);
                // 插入到用户事件表格顶部
                if (userEventsEl.firstChild) {
                    userEventsEl.insertBefore(row, userEventsEl.firstChild);
                } else {
                    userEventsEl.innerHTML = '';
                    userEventsEl.appendChild(row);
                }
                break;
                
            case 'PropertyRegistered':
                row = createPropertyEventRow(event);
                // 插入到房源事件表格顶部
                if (propertyEventsEl.firstChild) {
                    propertyEventsEl.insertBefore(row, propertyEventsEl.firstChild);
                } else {
                    propertyEventsEl.innerHTML = '';
                    propertyEventsEl.appendChild(row);
                }
                break;
                
            case 'BookingCreated':
            case 'BookingConfirmed':
            case 'BookingCompleted':
                row = createBookingEventRow(event);
                // 插入到预订事件表格顶部
                if (bookingEventsEl.firstChild) {
                    bookingEventsEl.insertBefore(row, bookingEventsEl.firstChild);
                } else {
                    bookingEventsEl.innerHTML = '';
                    bookingEventsEl.appendChild(row);
                }
                break;
                
            case 'ReviewSubmitted':
                row = createReviewEventRow(event);
                // 插入到评价事件表格顶部
                if (reviewEventsEl.firstChild) {
                    reviewEventsEl.insertBefore(row, reviewEventsEl.firstChild);
                } else {
                    reviewEventsEl.innerHTML = '';
                    reviewEventsEl.appendChild(row);
                }
                break;
        }
        
        // 创建通用事件行并插入到所有事件表格顶部
        const allEventRow = createEventRow(event);
        if (allEventsEl.firstChild) {
            allEventsEl.insertBefore(allEventRow, allEventsEl.firstChild);
        } else {
            allEventsEl.innerHTML = '';
            allEventsEl.appendChild(allEventRow);
        }
        
        // 更新合约信息
        loadContractInfo();
        
        // 显示通知
        showNotification(`新${getEventTypeName(eventType)}事件`);
    } catch (error) {
        console.error('处理新事件失败:', error);
    }
}

// 获取事件类型的中文名称
function getEventTypeName(eventType) {
    const eventTypeNames = {
        'UserRegistered': '用户注册',
        'PropertyRegistered': '房源注册',
        'BookingCreated': '预订创建',
        'BookingConfirmed': '预订确认',
        'BookingCompleted': '预订完成',
        'ReviewSubmitted': '评价提交'
    };
    return eventTypeNames[eventType] || eventType;
}

// 创建通用事件行
function createEventRow(event) {
    const row = document.createElement('tr');
    
    // 根据事件类型获取相关方和详情
    let relatedParty = '';
    let details = '';
    
    switch (event.type) {
        case 'UserRegistered':
            relatedParty = formatAddressWithLink(event.data.user);
            details = `用户名: ${event.data.name}`;
            break;
            
        case 'PropertyRegistered':
            relatedParty = formatAddressWithLink(event.data.owner);
            details = `房源ID: ${event.data.propertyId}, 标题: ${event.data.title}`;
            break;
            
        case 'BookingCreated':
            relatedParty = formatAddressWithLink(event.data.tenant);
            details = `预订ID: ${event.data.bookingId}, 房源ID: ${event.data.propertyId}`;
            break;
            
        case 'BookingConfirmed':
            // 预订确认事件没有相关方信息，我们可以留空或显示"--"
            relatedParty = '--';
            details = `预订ID: ${event.data.bookingId}`;
            break;
            
        case 'BookingCompleted':
            // 预订完成事件没有相关方信息，我们可以留空或显示"--"
            relatedParty = '--';
            details = `预订ID: ${event.data.bookingId}`;
            break;
            
        case 'ReviewSubmitted':
            relatedParty = formatAddressWithLink(event.data.reviewer);
            details = `房源ID: ${event.data.propertyId}, 评分: ${event.data.rating}`;
            break;
            
        default:
            relatedParty = '--';
            details = '--';
    }
    
    row.innerHTML = `
        <td>${formatTimestamp(event.timestamp)}</td>
        <td><span class="badge bg-primary">${getEventTypeName(event.type)}</span></td>
        <td>${relatedParty}</td>
        <td>${details}</td>
        <td>${formatTxHash(event.txHash)}</td>
    `;
    
    return row;
}

// 创建用户注册事件行
function createUserEventRow(event) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${formatTimestamp(event.timestamp)}</td>
        <td>${formatAddressWithLink(event.data.user)}</td>
        <td>${event.data.name}</td>
        <td>${formatTxHash(event.txHash)}</td>
    `;
    return row;
}

// 创建房源注册事件行
function createPropertyEventRow(event) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${formatTimestamp(event.timestamp)}</td>
        <td>${event.data.propertyId}</td>
        <td>${formatAddressWithLink(event.data.owner)}</td>
        <td>${event.data.title}</td>
        <td>${formatTxHash(event.txHash)}</td>
    `;
    return row;
}

// 创建预订事件行
function createBookingEventRow(event) {
    const row = document.createElement('tr');
    
    // 确定预订状态
    let status = '';
    switch (event.type) {
        case 'BookingCreated':
            status = '<span class="status-badge status-pending">待确认</span>';
            break;
        case 'BookingConfirmed':
            status = '<span class="status-badge status-confirmed">已确认</span>';
            break;
        case 'BookingCompleted':
            status = '<span class="status-badge status-completed">已完成</span>';
            break;
    }
    
    // 如果有租户信息则显示，否则显示"--"（确认和完成事件可能没有租户信息）
    const tenant = event.data.tenant 
        ? formatAddressWithLink(event.data.tenant)
        : '--';
    
    // 如果有房源ID则显示，否则显示"--"（确认和完成事件可能没有房源ID）
    const propertyId = event.data.propertyId !== undefined
        ? event.data.propertyId
        : '--';
    
    row.innerHTML = `
        <td>${formatTimestamp(event.timestamp)}</td>
        <td>${event.data.bookingId}</td>
        <td>${propertyId}</td>
        <td>${tenant}</td>
        <td>${status}</td>
        <td>${formatTxHash(event.txHash)}</td>
    `;
    return row;
}

// 创建评价事件行
function createReviewEventRow(event) {
    // 将评分显示为星星
    const stars = '★'.repeat(Number(event.data.rating)) + '☆'.repeat(5 - Number(event.data.rating));
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${formatTimestamp(event.timestamp)}</td>
        <td>${event.data.propertyId}</td>
        <td>${formatAddressWithLink(event.data.reviewer)}</td>
        <td><span class="rating-stars">${stars}</span> (${event.data.rating}/5)</td>
        <td>${formatTxHash(event.txHash)}</td>
    `;
    return row;
}

// 设置表格为加载状态
function setLoading(tableElement) {
    tableElement.innerHTML = '<tr><td colspan="6" class="text-center py-3">加载中...</td></tr>';
}

// 显示错误信息
function showError(message) {
    // 创建错误提示元素
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        <i class="bi bi-exclamation-triangle-fill me-2"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="关闭"></button>
    `;
    
    // 插入到页面顶部
    const mainContent = document.querySelector('main');
    mainContent.insertBefore(errorDiv, mainContent.firstChild);
    
    // 5秒后自动关闭
    setTimeout(() => {
        errorDiv.classList.remove('show');
        setTimeout(() => errorDiv.remove(), 500);
    }, 5000);
}

// 显示通知
function showNotification(message) {
    // 创建通知元素
    const notificationDiv = document.createElement('div');
    notificationDiv.className = 'alert alert-info alert-dismissible fade show';
    notificationDiv.innerHTML = `
        <i class="bi bi-info-circle-fill me-2"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="关闭"></button>
    `;
    
    // 插入到页面顶部
    const mainContent = document.querySelector('main');
    mainContent.insertBefore(notificationDiv, mainContent.firstChild);
    
    // 3秒后自动关闭
    setTimeout(() => {
        notificationDiv.classList.remove('show');
        setTimeout(() => notificationDiv.remove(), 500);
    }, 3000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initBlockchain); 