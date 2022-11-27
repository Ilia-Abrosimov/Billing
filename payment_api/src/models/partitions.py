import datetime
from typing import Tuple

from sqlalchemy import event
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.sql.ddl import DDL


class PartitionByMonthMeta(DeclarativeMeta):
    def __new__(cls, clsname, bases, attrs, *, partition_by):
        @classmethod
        def get_partition_name(cls_, key):
            return f'{cls_.__tablename__}_{key[0]}'

        @classmethod
        def create_partition(cls_, key: Tuple[str, str, str] = None):
            if not key:
                dt = datetime.date.today()
                key = [
                    f"y{dt.year}m{dt.month}",
                    dt.isoformat(),
                    (dt.replace(
                        day=1) +
                        datetime.timedelta(
                        days=32)).replace(
                        day=1).isoformat()]
            if key[0] not in cls_.partitions:
                Partition = type(
                    f'{clsname}{key[0]}',
                    bases,
                    {'__tablename__': cls_.get_partition_name(key)}
                )
                Partition.__table__.add_is_dependent_on(cls_.__table__)

                event.listen(
                    Partition.__table__,
                    'after_create',
                    DDL(
                        f"""
                        ALTER TABLE {cls_.__tablename__}
                        ATTACH PARTITION {Partition.__tablename__}
                        FOR VALUES FROM ('{key[1]}') TO ('{key[2]}');
                        """
                    )
                )

                cls_.partitions[key[0]] = Partition
            return cls_.partitions[key[0]]

        attrs.update(
            {
                '__table_args__': attrs.get('__table_args__', ())
                + (dict(postgresql_partition_by=f'RANGE({partition_by})'),),
                'partitions': {},
                'partitioned_by': partition_by,
                'get_partition_name': get_partition_name,
                'create_partition': create_partition
            }
        )

        return super().__new__(cls, clsname, bases, attrs)
