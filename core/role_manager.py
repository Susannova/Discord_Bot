import discord


class RoleManager:
    def __init__(self, ctx) -> None:
        self.ctx = ctx

    async def create_role(self, role_name) -> int:
        guild = self.ctx.guild
        existing_role = discord.utils.get(guild.roles, name=role_name)

        if existing_role:
            await self.ctx.send(f'Role "{role_name}" already exists.')
            return existing_role.id
        else:
            try:
                new_role = await guild.create_role(name=role_name)
                await self.ctx.send(f'Role "{new_role.name}" has been created.')
                return new_role.id
            except discord.HTTPException as e:
                await self.ctx.send(f"Failed to create role: {e}")
                return -1

    async def remove_role_by_id(self, role_id):
        guild = self.ctx.guild
        role_to_remove = discord.utils.get(guild.roles, id=role_id)

        if role_to_remove:
            try:
                await role_to_remove.delete()
                await self.ctx.send(f'Role "{role_id}" has been removed.')
            except discord.HTTPException as e:
                await self.ctx.send(f"Failed to remove role: {e}")
        else:
            await self.ctx.send(f'Role "{role_id}" not found.')
