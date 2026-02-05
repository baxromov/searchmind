import { Link, useLocation } from 'react-router-dom';
import { Search, Upload, Database } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/search', icon: Search, label: 'Search' },
    { path: '/knowledge-base', icon: Database, label: 'Knowledge Base' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <Search size={32} className="sidebar-brand-icon" />
        <span className="sidebar-brand-name">SearchMind</span>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;
