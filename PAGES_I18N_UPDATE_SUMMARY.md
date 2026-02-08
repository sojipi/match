# 页面多语言更新总结

## 已更新的组件

### ✅ 核心组件
1. **AppLayout** (`frontend/src/components/layout/AppLayout.tsx`)
   - 添加了 `useTranslation` hook
   - 导航菜单项现在使用翻译键
   - 所有导航文本支持多语言

2. **SettingsPage** (`frontend/src/pages/SettingsPage.tsx`)
   - 添加了 `useTranslation` hook
   - 标题和标签页使用翻译
   - 包含语言测试组件

3. **Dashboard** (`frontend/src/pages/Dashboard.tsx`)
   - 添加了 `useTranslation` hook
   - 欢迎消息使用翻译
   - 加载状态使用翻译

4. **MatchesPage** (`frontend/src/pages/MatchesPage.tsx`)
   - 添加了 `useTranslation` hook
   - 准备好使用翻译键

### 🔧 配置文件
5. **i18n Config** (`frontend/src/i18n/config.ts`)
   - 禁用了 Suspense
   - 启用了调试模式
   - 在 window 对象上暴露 i18n 实例

### 🧪 测试组件
6. **LanguageTest** (`frontend/src/components/LanguageTest.tsx`)
   - 新建的语言测试组件
   - 显示当前语言和翻译示例
   - 提供快速切换按钮

## 如何在其他页面中添加翻译支持

### 步骤 1: 导入 useTranslation

```typescript
import { useTranslation } from 'react-i18next';
```

### 步骤 2: 在组件中使用

```typescript
const MyComponent: React.FC = () => {
    const { t } = useTranslation();
    
    // 使用翻译
    return <h1>{t('navigation.dashboard')}</h1>;
};
```

### 步骤 3: 替换硬编码文本

```typescript
// 之前
<Typography>Dashboard</Typography>
<Button>Save</Button>
<Alert>Loading...</Alert>

// 之后
<Typography>{t('navigation.dashboard')}</Typography>
<Button>{t('common.save')}</Button>
<Alert>{t('common.loading')}</Alert>
```

## 常用翻译键参考

### 通用
- `common.welcome` - 欢迎
- `common.loading` - 加载中...
- `common.error` - 错误
- `common.success` - 成功
- `common.save` - 保存
- `common.cancel` - 取消
- `common.delete` - 删除
- `common.edit` - 编辑
- `common.back` - 返回
- `common.next` - 下一步
- `common.submit` - 提交
- `common.close` - 关闭

### 导航
- `navigation.home` - 首页
- `navigation.dashboard` - 控制台/仪表板
- `navigation.discover` - 发现
- `navigation.matches` - 匹配
- `navigation.messages` - 消息
- `navigation.notifications` - 通知
- `navigation.profile` - 个人资料
- `navigation.settings` - 设置
- `navigation.avatar` - 我的化身

### 认证
- `auth.login` - 登录
- `auth.logout` - 退出
- `auth.register` - 注册
- `auth.email` - 电子邮箱
- `auth.password` - 密码

### 匹配
- `matching.discover` - 发现匹配
- `matching.compatibility` - 兼容性
- `matching.like` - 喜欢
- `matching.pass` - 跳过
- `matching.startConversation` - 开始对话

### 消息
- `messages.conversations` - 对话
- `messages.newMessage` - 新消息
- `messages.sendMessage` - 发送消息
- `messages.online` - 在线
- `messages.offline` - 离线

### 通知
- `notifications.title` - 通知
- `notifications.markAllRead` - 全部标记为已读
- `notifications.noNotifications` - 暂无通知

### 个人资料
- `profile.editProfile` - 编辑资料
- `profile.basicInfo` - 基本信息
- `profile.photos` - 照片
- `profile.bio` - 个人简介

### 设置
- `settings.title` - 设置
- `settings.language` - 语言
- `settings.theme` - 主题
- `settings.accessibility` - 无障碍
- `settings.privacy` - 隐私

### 错误
- `errors.generic` - 出错了，请重试
- `errors.network` - 网络错误
- `errors.authentication` - 认证失败

## 待更新的页面列表

### 高优先级
- [ ] `MessagesPage.tsx` - 消息页面
- [ ] `ProfileManagementPage.tsx` - 个人资料管理
- [ ] `NotificationsPage.tsx` - 通知页面
- [ ] `MatchDiscoveryPage.tsx` - 匹配发现页面

### 中优先级
- [ ] `PersonalityAssessmentPage.tsx` - 性格评估
- [ ] `AvatarPage.tsx` - AI化身页面
- [ ] `CompatibilityReportPage.tsx` - 兼容性报告
- [ ] `LiveMatchingTheaterPage.tsx` - 实时匹配剧场

### 低优先级
- [ ] `LandingPage.tsx` - 落地页
- [ ] `AuthPage.tsx` - 认证页面
- [ ] 各种子组件

## 快速更新模板

复制以下代码到任何需要更新的页面：

```typescript
// 1. 在文件顶部添加导入
import { useTranslation } from 'react-i18next';

// 2. 在组件内部添加 hook
const MyPage: React.FC = () => {
    const { t } = useTranslation();
    
    // 3. 使用 t() 函数替换文本
    return (
        <Box>
            <Typography variant="h4">{t('navigation.dashboard')}</Typography>
            <Button>{t('common.save')}</Button>
        </Box>
    );
};
```

## 测试清单

更新页面后，请测试：

- [ ] 页面加载正常
- [ ] 切换语言后文本立即更新
- [ ] 所有按钮和标签都显示正确的翻译
- [ ] 没有显示翻译键（如 "navigation.dashboard"）
- [ ] 在浏览器控制台没有 i18n 错误

## 注意事项

1. **不要硬编码文本**：所有用户可见的文本都应该使用 `t()` 函数
2. **检查翻译键是否存在**：确保使用的键在所有6种语言文件中都有定义
3. **使用插值**：对于动态内容，使用插值语法：
   ```typescript
   t('dashboard.welcome', { name: user.name })
   ```
4. **复数形式**：i18next 支持复数形式，查看文档了解更多
5. **保持一致性**：使用相同的翻译键来表示相同的概念

## 验证方法

1. 打开页面
2. 打开设置 → Language & Culture
3. 使用语言测试组件切换语言
4. 检查页面文本是否更新
5. 导航到其他页面，确认语言保持一致

## 需要帮助？

如果遇到问题：
1. 检查浏览器控制台的错误信息
2. 确认翻译键在 `translation.json` 文件中存在
3. 确认组件正确导入和使用了 `useTranslation`
4. 查看 `LANGUAGE_SWITCHING_DEBUG.md` 获取详细调试步骤
