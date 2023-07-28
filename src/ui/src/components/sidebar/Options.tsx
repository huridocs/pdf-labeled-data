import React, { useContext } from 'react';
import styled from 'styled-components';
import { Switch } from '@allenai/varnish';

import { CheckOutlined, CloseOutlined } from '@ant-design/icons';

import { SidebarItem, SidebarItemTitle } from './common';
import { OptionsStore, SHOW_TOKENS } from '../../context/OptionsStore';

export const Options = () => {
    const { options, setOptions } = useContext(OptionsStore);

    const onToggleShowTokens = async () => {
        const newValue = !options[SHOW_TOKENS];
        setOptions({ ...options, [SHOW_TOKENS]: newValue });
    };

    return (
        <SidebarItem>
            <SidebarItemTitle>Options</SidebarItemTitle>
            <Container>
                <div>
                    Show tokens
                    <Toggle
                        size="small"
                        onChange={onToggleShowTokens}
                        checkedChildren={<CheckOutlined />}
                        unCheckedChildren={<CloseOutlined />}
                        checked={options[SHOW_TOKENS]}
                    />
                </div>
            </Container>
        </SidebarItem>
    );
};

const Toggle = styled(Switch)`
    margin: 4px;
`;

const Container = styled.div(
    ({ theme }) => `
   margin-top: ${theme.spacing.sm};
   div + div {
       margin-top: ${theme.spacing.sm};
   }

`
);
