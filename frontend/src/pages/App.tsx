import { Layout, Menu } from "antd";
import { Outlet, useNavigate } from "react-router-dom";
import { useEffect } from "react";

const { Header, Sider, Content } = Layout;

export default function App() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) navigate("/login");
  }, [navigate]);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider>
        <div style={{ color: "#fff", padding: 16, fontWeight: 600 }}>后台管理</div>
        <Menu
          theme="dark"
          mode="inline"
          onClick={(e) => navigate(e.key)}
          items={[
            { key: "/", label: "仪表盘" },
            { key: "/products", label: "产品" },
            { key: "/import", label: "导入" },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ background: "#fff" }} />
        <Content style={{ padding: 16 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
