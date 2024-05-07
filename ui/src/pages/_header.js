
import { Menu } from 'antd';
import Image from 'next/image';

export default function Header() {
    
    return (
      <div className="page-header">
        <Menu mode="horizontal" 
          className="header">
          <div className="header-title">
            <h1>Haiven</h1>
            <h2>Team assistant</h2>
            
          </div>
          <div className="header-logo">
          
            <a href="https://www.thoughtworks.com">
              {/* 400, 65 */}
              {/* 280, 45 */}
              <Image alt="Thoughtworks" id="tw-logo" src="/boba/thoughtworks_logo.png" title="Thoughtworks" width={160} height={26}/>
            </a>
          </div>
        </Menu>
      </div>
    );
  
}