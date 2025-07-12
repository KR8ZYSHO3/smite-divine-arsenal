# 🎮 SMITE 2 Divine Arsenal - Community Features

Welcome to the enhanced Divine Arsenal with full community integration! This system allows SMITE 2 players to connect, chat, form parties, and build a thriving community around the game.

## 🌟 Features Overview

### 🔐 Authentication System
- **Tracker.gg Integration**: Login with your SMITE 2 Tracker.gg profile
- **Automatic Profile Sync**: Your stats, rank, and favorite gods are automatically imported
- **Secure JWT Tokens**: Industry-standard authentication with session management
- **Profile Management**: Update your bio, favorite roles, and social links

### 👥 Community Dashboard
- **Real-time Online Players**: See who's currently online and available to play
- **Player Search**: Find players by username or role preference
- **Friend System**: Add friends and manage your connections
- **Activity Tracking**: Monitor community engagement and statistics

### 💬 Chat System
- **Global Chat**: Community-wide discussions about SMITE 2
- **Party Chat**: Private chat rooms for party members
- **Direct Messages**: Private conversations between friends
- **Message History**: Persistent chat history with search functionality

### 🎯 Party System
- **Create Parties**: Form groups for specific game modes or skill levels
- **Public/Private Parties**: Choose visibility for your parties
- **Role-based Matching**: Find players by their preferred roles
- **Party Management**: Invite, kick, and transfer leadership
- **Game Session Tracking**: Monitor active games and party status

### 📊 Community Analytics
- **Real-time Statistics**: Online users, active parties, message activity
- **Role Distribution**: See which roles are most popular
- **Activity Metrics**: Track community engagement over time
- **Performance Insights**: Community health and growth indicators

## 🚀 Getting Started

### 1. Installation

Install the required dependencies:

```bash
cd divine_arsenal/backend
pip install -r requirements.txt
```

### 2. Database Setup

The community system automatically creates the necessary database tables when first initialized. No manual setup required!

### 3. Launch the Application

```bash
python app.py
```

### 4. Access the Community Dashboard

Navigate to `http://localhost:5000/community` to access the community dashboard.

## 🔧 API Endpoints

### Authentication
- `POST /api/community/auth/login` - Login with Tracker.gg username
- `POST /api/community/auth/logout` - Logout user
- `GET /api/community/auth/profile` - Get current user profile

### Users
- `GET /api/community/users/online` - Get online users
- `GET /api/community/users/search?q=<query>` - Search users
- `GET /api/community/users/by-role/<role>` - Get users by role

### Chat
- `GET /api/community/chat/messages/<room_id>` - Get chat messages
- `POST /api/community/chat/send` - Send a message

### Parties
- `GET /api/community/parties` - Get public parties
- `POST /api/community/parties` - Create a new party
- `POST /api/community/parties/<party_id>/join` - Join a party
- `POST /api/community/parties/<party_id>/leave` - Leave a party
- `GET /api/community/parties/<party_id>/members` - Get party members
- `GET /api/community/parties/my` - Get user's parties

### Friends
- `GET /api/community/friends` - Get friends list
- `POST /api/community/friends/add` - Add a friend

### Statistics
- `GET /api/community/stats` - Get community statistics
- `GET /api/community/health` - Health check endpoint

## 💻 Frontend Integration

The community dashboard is built with modern HTML, CSS, and JavaScript:

### Key Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live chat and user status updates
- **Modern UI**: Beautiful gradient backgrounds and glass-morphism effects
- **Interactive Elements**: Hover effects, animations, and smooth transitions

### Customization
The dashboard can be customized by modifying:
- `divine_arsenal/templates/community_dashboard.html` - Main template
- CSS styles in the `<style>` section
- JavaScript functionality in the `<script>` section

## 🔒 Security Features

### Authentication Security
- **JWT Tokens**: Secure, stateless authentication
- **Session Management**: Automatic token expiration and renewal
- **Rate Limiting**: Protection against abuse and spam
- **Input Validation**: Sanitized user inputs and SQL injection protection

### Data Protection
- **Encrypted Storage**: Sensitive data is properly encrypted
- **Privacy Controls**: Users control their profile visibility
- **Activity Logging**: Comprehensive audit trails for moderation

## 🎮 SMITE 2 Integration

### Tracker.gg Sync
- **Profile Import**: Automatic import of SMITE 2 stats and rank
- **Recent Matches**: Analysis of recent gameplay for role preferences
- **Performance Metrics**: Integration with player performance data
- **Real-time Updates**: Sync with Tracker.gg for latest stats

### Game Integration
- **Role Matching**: Find players based on SMITE 2 roles (Solo, Jungle, Mid, ADC, Support)
- **Game Mode Support**: Conquest, Arena, Joust, and other modes
- **Skill Level Matching**: Casual, competitive, and mixed skill levels
- **Build Sharing**: Share and discuss optimal builds within the community

## 📈 Community Management

### Moderation Tools
- **Message Filtering**: Automatic detection of inappropriate content
- **User Reporting**: Report system for community violations
- **Admin Panel**: Community management interface (coming soon)
- **Activity Monitoring**: Track community health and engagement

### Analytics Dashboard
- **User Growth**: Track community expansion over time
- **Engagement Metrics**: Message activity, party formation, user retention
- **Role Distribution**: Monitor which SMITE 2 roles are most popular
- **Peak Hours**: Identify when the community is most active

## 🔧 Configuration

### Environment Variables
```bash
# JWT Secret Key (auto-generated if not set)
JWT_SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_PATH=divine_arsenal/backend/divine_arsenal.db

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_HOUR=100
```

### Database Schema
The community system creates the following tables:
- `users` - User profiles and authentication data
- `user_sessions` - Active user sessions and tokens
- `user_friends` - Friend relationships and requests
- `chat_messages` - Chat message history
- `online_status` - Real-time user online status
- `parties` - Party information and settings
- `party_members` - Party membership and roles
- `game_sessions` - Active game sessions
- `user_activity` - User activity logging

## 🚀 Future Enhancements

### Planned Features
- **Voice Chat**: Integrated voice communication for parties
- **Tournament System**: Community-organized tournaments and events
- **Achievement System**: Community achievements and badges
- **Mobile App**: Native mobile application for iOS and Android
- **Discord Integration**: Connect with Discord servers and bots
- **Stream Integration**: Twitch and YouTube streamer integration
- **Pro Team Support**: Professional team and player profiles

### Technical Improvements
- **WebSocket Support**: Real-time bidirectional communication
- **Push Notifications**: Mobile and browser notifications
- **Advanced Search**: Full-text search across messages and profiles
- **File Sharing**: Image and build file sharing in chat
- **API Rate Limiting**: Advanced rate limiting and abuse prevention

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow PEP 8 Python style guidelines
- Add type hints to all functions
- Include comprehensive docstrings
- Write unit tests for new features
- Update documentation for API changes

## 📞 Support

### Getting Help
- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests on GitHub
- **Community**: Join our Discord server for community support
- **Email**: Contact the development team for technical support

### Troubleshooting

#### Common Issues
1. **JWT Import Error**: Install PyJWT with `pip install PyJWT`
2. **Database Errors**: Ensure write permissions for the database directory
3. **Tracker.gg Connection**: Check internet connection and Tracker.gg availability
4. **Rate Limiting**: Reduce request frequency if hitting rate limits

#### Performance Optimization
- **Database Indexing**: Automatic index creation for optimal query performance
- **Caching**: Implement Redis caching for frequently accessed data
- **Connection Pooling**: Optimize database connection management
- **CDN Integration**: Use CDN for static assets and improved loading times

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Tracker.gg**: For providing SMITE 2 player data and statistics
- **SMITE 2 Community**: For feedback and feature suggestions
- **Open Source Contributors**: For the libraries and tools that make this possible

---

**Ready to join the SMITE 2 Divine Arsenal community?** 🎮⚔️

Visit `http://localhost:5000/community` to get started! 