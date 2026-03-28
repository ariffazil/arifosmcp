from arifosmcp.core.organs._0_init import init as organ_init, AuthorityLevel
from arifosmcp.core.shared.types import InitOutput


class AnchorEngine:
    async def ignite(
        self, query: str, actor_id: str = "anonymous", auth_token: str | None = None, **kwargs
    ) -> InitOutput:
        return await organ_init(query, actor_id, auth_token=auth_token, **kwargs)


anchor_engine = AnchorEngine()


async def init_000_anchor(query: str, actor_id: str = "user", **kwargs) -> InitOutput:
    return await anchor_engine.ignite(query, actor_id, **kwargs)
